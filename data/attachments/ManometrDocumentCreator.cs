using System.Reflection;
using Infrastructure.DocumentProcessor.Forms;
using ProjApp.ProtocolForms;
using PuppeteerSharp;

namespace Infrastructure.DocumentProcessor.Creator;

internal class ManometrSuccessDocumentCreator : DocumentCreatorBase<ManometrForm>
{
    protected override IReadOnlyList<PropertyInfo> TypeProps { get; init; } = typeof(ManometrForm).GetProperties();

    public ManometrSuccessDocumentCreator(
        Browser browser,
        Dictionary<string, string> signsCache,
        string signsDirPath)
            : base(browser,
                   signsCache,
                   signsDirPath,
                   HTMLForms.Manometr)
    { }

    protected override async Task<string?> SetSpecificAsync(IPage page, ManometrForm data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name == "MeasurementUnit");
        if (prop == null) return "MeasurementUnit prop not found";

        var measurement1Element = await page.QuerySelectorAsync("#measurementUnit1");
        if (measurement1Element == null) return "measurementUnit1 not found";
        await measurement1Element.SetElementValueAsync(prop.GetValue(data)!.ToString()!);

        var measurement2Element = await page.QuerySelectorAsync("#measurementUnit2");
        if (measurement2Element == null) return "measurementUnit2 not found";
        await measurement2Element.SetElementValueAsync(prop.GetValue(data)!.ToString()!);

        var table = await page.QuerySelectorAsync("#valuesTable");
        if (table == null)
        {
            return "Table not found";
        }

        var tbody = await table.QuerySelectorAsync("tbody");
        if (tbody == null)
        {
            return "Table body not found";
        }

        var columnFormats = new Dictionary<int, string>
        {
            { 0, "N2" }, // Показания поверяемого СИ (прямой ход)
            { 1, "N2" }, // Показания поверяемого СИ (обратный ход)
            { 2, "N3" }, // Показания эталона (прямой ход)
            { 3, "N3" }, // Показания эталона (обратный ход)
            { 4, "N2" }, // Приведенная погрешность (прямой ход)
            { 5, "N2" }, // Приведенная погрешность (обратный ход)
            { 6, "N2" }, // Допустимая приведенная погрешность
            { 7, "N2" }, // Вариация показаний
            { 8, "N2" }  // Допустимая вариация
        };

        for (int rowIndex = 0; rowIndex < 8; rowIndex++)
        {
            var rows = await tbody.QuerySelectorAllAsync("tr");
            if (rowIndex >= rows.Length) continue;

            var row = rows[rowIndex];
            if (row == null) continue;

            for (int colIndex = 0; colIndex < 9; colIndex++)
            {
                var cell = await row.QuerySelectorAsync($"td:nth-child({colIndex + 1})");
                if (cell == null) continue;

                var innerHtml = await cell.EvaluateFunctionAsync<string>("el => el.innerHTML");
                if (innerHtml.Trim() == "-") continue;

                var value = colIndex switch
                {
                    0 => data.DeviceValues[0][rowIndex],
                    1 => data.DeviceValues[1][rowIndex],
                    2 => data.EtalonValues[0][rowIndex],
                    3 => data.EtalonValues[1][rowIndex],
                    4 => data.ActualError[0][rowIndex],
                    5 => data.ActualError[1][rowIndex],
                    6 => data.ValidError,
                    7 => data.ActualVariation[rowIndex],
                    8 => data.ValidError,
                    _ => throw new Exception("Некорректный индекс столбца")
                };

                await cell.SetElementValueAsync(value.ToString(), columnFormats[colIndex]);
            }
        }

        return null;
    }
}
