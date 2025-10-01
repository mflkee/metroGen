using PuppeteerSharp;

namespace Infrastructure.DocumentProcessor.Creator;

internal static class PageManipulationExtensions
{
    public static async Task<(bool Success, string RemainingText)> SetElementTextExactAsync(this IPage page, string selector, string text)
    {
        try
        {
            var result = await page.EvaluateFunctionAsync<TextFitResult>(@"(selector, fullText) => {
            const element = document.querySelector(selector);
            if (!element) return { success: false, fittedText: '', remainingText: fullText };

            // Save original styles for measurement
            const style = window.getComputedStyle(element);
            const maxWidth = element.clientWidth;
            const maxHeight = element.clientHeight;
            
            // Create measurement element with identical styling
            const measurer = element.cloneNode(true);
            measurer.style.position = 'absolute';
            measurer.style.visibility = 'hidden';
            document.body.appendChild(measurer);

            // Find last space position where text fits
            let lastValidSpace = -1;
            let currentPosition = 0;
            let remainingText = fullText;
            let fittedText = '';

            // Check whole text first
            measurer.textContent = fullText;
            if (measurer.scrollWidth <= maxWidth && measurer.scrollHeight <= maxHeight) {
                element.textContent = fullText;
                document.body.removeChild(measurer);
                return { 
                    success: true, 
                    fittedText: fullText, 
                    remainingText: '' 
                };
            }

            // Find the optimal split point at a space boundary
            while (currentPosition < fullText.length) {
                const nextSpace = fullText.indexOf(' ', currentPosition);
                if (nextSpace === -1) break;
                
                const testText = fullText.substring(0, nextSpace);
                measurer.textContent = testText;
                
                if (measurer.scrollWidth <= maxWidth && measurer.scrollHeight <= maxHeight) {
                    lastValidSpace = nextSpace;
                    currentPosition = nextSpace + 1;
                } else {
                    break;
                }
            }

            // Prepare results
            if (lastValidSpace > 0) {
                fittedText = fullText.substring(0, lastValidSpace);
                remainingText = fullText.substring(lastValidSpace + 1);
                element.textContent = fittedText;
            } else {
                // No space found - return failure
                remainingText = fullText;
            }

            // Clean up
            document.body.removeChild(measurer);
            
            return { 
                success: lastValidSpace > 0,
                fittedText: fittedText,
                remainingText: remainingText
            };
        }", selector, text);

            return (result.Success, result.RemainingText);
        }
        catch
        {
            return (false, text);
        }
    }

    public static async Task<bool> SetElementTextAsync(this IPage page, string selector, string text)
    {
        try
        {
            return await page.EvaluateFunctionAsync<bool>(@"(selector, text) => {
            const originalElement = document.querySelector(selector);
            if (!originalElement) return false;

            // Cache DOM references
            const parent = originalElement.parentNode;
            const staticTextElement = originalElement.nextElementSibling;
            const originalClass = originalElement.className;
            const originalStyle = originalElement.getAttribute('style');
            
            // Get dimensions once
            const rect = originalElement.getBoundingClientRect();
            const maxWidth = rect.width;
            
            // Create canvas for faster measurement
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const style = window.getComputedStyle(originalElement);
            ctx.font = style.font;
            
            // Pre-process text into words and spaces
            const tokens = [];
            let buffer = '';
            let isWord = false;
            
            for (let i = 0; i < text.length; i++) {
                const char = text[i];
                const charIsSpace = char.trim() === '';
                
                if (charIsSpace !== isWord) {
                    if (buffer) tokens.push(buffer);
                    buffer = char;
                    isWord = !charIsSpace;
                } else {
                    buffer += char;
                }
            }
            if (buffer) tokens.push(buffer);

            // Process tokens
            let currentElement = originalElement;
            originalElement.textContent = '';
            let currentLine = [];
            let currentWidth = 0;
            let hasPassedStaticText = false;

            const createElement = () => {
                const el = document.createElement(originalElement.tagName);
                el.className = originalClass;
                if (originalStyle) el.setAttribute('style', originalStyle);
                
                if (!hasPassedStaticText && staticTextElement) {
                    parent.insertBefore(el, staticTextElement.nextSibling);
                    hasPassedStaticText = true;
                } else {
                    parent.insertBefore(el, currentElement.nextSibling);
                }
                return el;
            };

            for (const token of tokens) {
                const tokenWidth = ctx.measureText(token).width;
                
                if (currentWidth + tokenWidth <= maxWidth) {
                    currentLine.push(token);
                    currentWidth += tokenWidth;
                } else {
                    // Commit current line
                    currentElement.textContent = currentLine.join('');
                    
                    // Handle overflow
                    if (tokenWidth > maxWidth) {
                        // For tokens wider than container (preserve whole token)
                        currentElement = createElement();
                        currentElement.textContent = token;
                        currentElement = createElement();
                    } else {
                        // Normal overflow
                        currentElement = createElement();
                        currentLine = [token];
                        currentWidth = tokenWidth;
                    }
                }
            }

            // Flush remaining content
            if (currentLine.length > 0) {
                currentElement.textContent = currentLine.join('');
            }

            return true;
        }", selector, text);
        }
        catch
        {
            return false;
        }
    }

    public static async Task SetElementValueAsync(this IElementHandle element, string value, string? format = null)
    {
        format ??= await element.EvaluateFunctionAsync<string>("el => el.getAttribute('data-format')");

        if (format != null)
        {
            if (format.StartsWith('N'))
            {
                var formattedValue = double.Parse(value).ToString(format);
                await element.EvaluateFunctionAsync("(el, val) => { el.innerHTML = val; }", formattedValue);
            }
            else if (format == "0%")
            {
                var formattedValue = double.Parse(value).ToString(format);
                await element.EvaluateFunctionAsync("(el, val) => { el.innerHTML = val; }", formattedValue);
            }
            else
            {
                throw new Exception($"Unsupported format: {format}");
            }
        }
        else
        {
            await element.EvaluateFunctionAsync("(el, val) => { el.innerHTML = val; }", value);
        }
    }

    public static async Task<string?> RemoveElementAsync(this IPage page, string selector)
    {
        try
        {
            await page.EvaluateFunctionAsync(@"(selector) => {
            const element = document.querySelector(selector);
            if (element && element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }", selector);
            return null;
        }
        catch (Exception ex)
        {
            return ex.Message;
        }
    }

    public class TextFitResult
    {
        public required bool Success { get; set; }
        public required string FittedText { get; set; }
        public required string RemainingText { get; set; }
    }
}

/*
    public async Task<HTMLCreationResult> CreateAsync(T data, CancellationToken? cancellationToken = null)
    {
        var config = Configuration.Default.WithDefaultLoader();
        using var context = BrowsingContext.New(config);
        using var document = await context.OpenAsync(r => r.Content(_htmlForm), cancellationToken ?? CancellationToken.None);

        var deviceInfoResult = SetDeviceInfo(document, data);
        if (deviceInfoResult != null) return HTMLCreationResult.Failure(deviceInfoResult);

        foreach (var idValueElement in document.QuerySelectorAll("[id]").Where(e => e.Id!.StartsWith("setValue_")))
        {
            var id = idValueElement.Id!["setValue_".Length..].ToLower();
            var prop = TypeProps.FirstOrDefault(t => t.Name.Equals(id, StringComparison.OrdinalIgnoreCase));
            if (prop == null) return HTMLCreationResult.Failure($"Data property {id} not found");
            SetElementValue(idValueElement, prop.GetValue(data)!.ToString()!);
        }

        var result = SetVerification(document, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = SetEtalons(document, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        result = SetCheckups(document, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        if (cancellationToken.HasValue &&
        cancellationToken.Value.IsCancellationRequested)
        {
            return HTMLCreationResult.Failure("Отмена");
        }

        result = await SetSignAsync(document, data);
        if (result != null) return HTMLCreationResult.Failure(result);

        var specifiResult = SetSpecific(document, data);
        if (specifiResult != null) return HTMLCreationResult.Failure(specifiResult);

        // return HTMLCreationResult.Success(document.DocumentElement.OuterHtml);
        return null!;
    }

    protected static void SetElementValue(IElement element, string value, string? format = null)
    {
        format ??= element.GetAttribute("data-format");
        if (format != null)
        {
            if (format.StartsWith('N'))
            {
                element.InnerHtml = double.Parse(value).ToString(format);
            }
            else if (format == "0%")
            {
                element.InnerHtml = double.Parse(value).ToString(format);
            }
            else
            {
                throw new Exception($"Неподдерживаемый формат: {format}");
            }
        }
        else
        {
            element.InnerHtml = value;
        }
    }

    protected string? SetLine(IHtmlParagraphElement element, int lineLength, ref string text)
    {
        if (text.Length <= lineLength)
        {
            // Text fits entirely
            element.InnerHtml = text;
            text = string.Empty;
            return null;
        }

        // Find the last space within maxLength+1 characters
        int splitPos = text.Substring(0, lineLength + 1).LastIndexOf(' ');

        if (splitPos > 0)
        {
            // Split at the found space
            element.InnerHtml = text.Substring(0, splitPos);
            text = text.Substring(splitPos + 1);
            return null;
        }

        return "Нет возможности разделить текст. Пробелы отсутствуют.";
    }

    private string? SetDeviceInfo(IDocument document, T data)
    {
        var deviceTypeNameElement = document.QuerySelector<IHtmlParagraphElement>("#manual_deviceInfo");
        if (deviceTypeNameElement == null) return "manual_deviceInfo not found";
        var insertAfterDeviceNameElement = deviceTypeNameElement.NextSibling;
        if (insertAfterDeviceNameElement == null) return "manual_deviceInfo sibling not found";
        var prop = TypeProps.FirstOrDefault(p => p.Name.Equals("deviceInfo", StringComparison.OrdinalIgnoreCase));
        if (prop == null) return "Data property deviceInfo not found";
        var deviceInfo = prop.GetValue(data)!.ToString()!;
        var deviceNameError = SetLine(deviceTypeNameElement, FullLineLength, ref deviceInfo);
        if (deviceNameError != null) return deviceNameError;

        while (deviceInfo.Length > 0)
        {
            var newDeviceNameLineElement = (IHtmlParagraphElement)deviceTypeNameElement.Clone(false);
            deviceNameError = SetLine(newDeviceNameLineElement, FullLineLength, ref deviceInfo);
            if (deviceNameError != null) return deviceNameError;
            insertAfterDeviceNameElement.InsertAfter(newDeviceNameLineElement);
            insertAfterDeviceNameElement = newDeviceNameLineElement;
        }

        return null;
    }

    private string? SetVerification(IDocument document, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name.Equals("verificationsinfo", StringComparison.OrdinalIgnoreCase));
        if (prop == null) return "Data property verificationsinfo not found";
        var verificationsText = prop.GetValue(data)!.ToString()!;
        var mainLine = document.QuerySelector<IHtmlParagraphElement>("#manual_verificationMethodMain")!;
        var result = SetLine(mainLine, VerificationLineLength, ref verificationsText);
        if (result != null) return result;
        if (verificationsText.Length == 0) return null;

        var vmAdditionalContainer = document.QuerySelector<IHtmlDivElement>("#manual_verificationMethodAdditional")!;

        while (verificationsText.Length > 0)
        {
            var element = document.CreateElement<IHtmlParagraphElement>();
            element.ClassName = "line";
            vmAdditionalContainer.AppendChild(element);
            SetLine(element, FullLineLength, ref verificationsText);
        }

        return null;
    }

    private string? SetEtalons(IDocument document, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name.Equals("EtalonsInfo", StringComparison.OrdinalIgnoreCase));
        if (prop == null) return "Data property EtalonsInfo not found";
        var etalonsText = prop.GetValue(data)!.ToString()!;

        var mainLine = document.QuerySelector<IHtmlParagraphElement>("#mainLine_etalons")!;
        var result = SetLine(mainLine, EtalonLineLength, ref etalonsText);
        if (result != null) return result;
        if (etalonsText.Length == 0) return null;

        var additionalLine = document.QuerySelector<IHtmlParagraphElement>("#additionalLine_etalons")!;
        result = SetLine(additionalLine, FullLineLength, ref etalonsText);
        if (result != null) return result;
        if (etalonsText.Length == 0) return null;

        var addAfterElement = document.QuerySelector("#addAfter_etalons")!;

        while (etalonsText.Length > 0)
        {
            var newLine = (IHtmlParagraphElement)additionalLine.Clone(false);
            result = SetLine(newLine, FullLineLength, ref etalonsText);
            if (result != null) return result;
            addAfterElement.InsertAfter(newLine);
            addAfterElement = newLine;
        }

        return null;
    }

    private string? SetCheckups(IDocument document, T data)
    {
        var verificationInfoProp = TypeProps.FirstOrDefault(p => p.Name.Equals("VerificationsInfo", StringComparison.OrdinalIgnoreCase));
        if (verificationInfoProp == null) return "Data property VerificationsInfo not found";
        var verificationInfo = verificationInfoProp.GetValue(data)!.ToString()!;

        var checkupsProp = TypeProps.FirstOrDefault(p => p.Name.Equals("Checkups", StringComparison.OrdinalIgnoreCase));
        if (checkupsProp == null) return "Data property Checkups not found";
        var checkups = (Dictionary<string, string>)checkupsProp.GetValue(data)!;

        var checkupElement = document.QuerySelector<IHtmlParagraphElement>("#manual_checkup");
        if (checkupElement == null) return "manual_checkup not found";

        var checkupNum = 1;

        foreach (var (key, value) in checkups)
        {
            var checkupNumElement = checkupElement.QuerySelector("#manual_checkupNum");
            if (checkupNumElement == null) return "manual_checkupNum not found";
            checkupNumElement.TextContent = $"{checkupNum++}. ";

            var checkupTitleElement = checkupElement.QuerySelector("#manual_checkupTitle");
            if (checkupTitleElement == null) return "manual_checkupTitle not found";
            checkupTitleElement.TextContent = key;

            var checkupValueElement = checkupElement.QuerySelector("#manual_checkupValue");
            if (checkupValueElement == null) return "manual_checkupValue not found";
            checkupValueElement.TextContent = value;

            var checkupVerificationElement = checkupElement.QuerySelector("#manual_checkupVerification");
            if (checkupVerificationElement != null)
            {
                checkupVerificationElement.TextContent = verificationInfo;
            }

            var newCheckupElement = (IHtmlParagraphElement)checkupElement.Clone(true);
            checkupElement.After(newCheckupElement);
            checkupElement = newCheckupElement;
        }

        checkupElement.Remove();

        return null;
    }

    private async Task<string?> SetSignAsync(IDocument document, T data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name == "Worker");
        if (prop == null) return "Data property Worker not found";
        var worker = (string)prop.GetValue(data)!;
        worker = worker.ToLower();

        if (!_signsCache.TryGetValue(worker, out var _))
        {
            var signFilesPaths = Directory.GetFiles(_signsDirPath, $"{worker}*.png");

            if (signFilesPaths.Length < 12) return $"Подпись сотрудника {worker} не найдена. Или вариантов меньше 12";

            foreach (var filePath in signFilesPaths)
            {
                var bytes = await File.ReadAllBytesAsync(filePath);
                var base64 = Convert.ToBase64String(bytes);
                var signBase64 = $"data:image/png;base64,{base64}";
                var cacheKey = Path.GetFileNameWithoutExtension(filePath);
                _signsCache[cacheKey] = signBase64;
            }
        }

        var signsCount = _signsCache.Where(s => s.Key.StartsWith(worker)).Count();
        var randomSignIndex = Random.Shared.Next(1, signsCount);
        var key = $"{worker} {randomSignIndex}";
        var _ = _signsCache.TryGetValue(key, out var sign);

        var imgElement = document.QuerySelector<IHtmlImageElement>("#sign")!;
        var randomTop = Random.Shared.Next(20, 30);
        var randomLeft = Random.Shared.Next(30, 150);
        var randomHeight = Random.Shared.Next(31, 33);
        imgElement.SetAttribute("style", $"top: {randomTop}px; left: {randomLeft}px;height: {randomHeight}px;");
        imgElement.Source = sign;

        return null;
    }

*/