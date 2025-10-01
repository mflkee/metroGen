using System.Reflection;
using Infrastructure.DocumentProcessor.Forms;
using ProjApp.ProtocolForms;
using PuppeteerSharp;

namespace Infrastructure.DocumentProcessor.Creator;

internal class DavlenieSuccessDocumentCreator : DocumentCreatorBase<DavlenieForm>
{
    protected override IReadOnlyList<PropertyInfo> TypeProps { get; init; } = typeof(DavlenieForm).GetProperties();

    public DavlenieSuccessDocumentCreator(
        Browser browser,
        Dictionary<string, string> signsCache,
        string signsDirPath)
            : base(browser,
                   signsCache,
                   signsDirPath,
                   HTMLForms.Davlenie)
    { }

    protected override async Task<string?> SetSpecificAsync(IPage page, DavlenieForm data)
    {
        var prop = TypeProps.FirstOrDefault(p => p.Name == "MeasurementUnit");
        if (prop == null) return "MeasurementUnit prop not found";

        var measurementElement = await page.QuerySelectorAsync("#measurementUnit");
        if (measurementElement == null) return "measurementUnit not found";
        await measurementElement.SetElementValueAsync(prop.GetValue(data)!.ToString()!);

        var table = await page.QuerySelectorAsync("#valuesTable");
        if (table == null) return "Таблица не найдена";

        var tbody = await table.QuerySelectorAsync("tbody");
        if (tbody == null) return "Таблица не содержит строк";

        var columnFormats = new Dictionary<int, string>
    {
        { 1, "N1" }, // Давление
        { 2, "N3" }, // Показания эталона
        { 3, "N3" }, // Показания устройства (прямой ход)
        { 4, "N3" }, // Показания устройства (обратный ход)
        { 5, "N3" }, // Приведенная погрешность (прямой ход)
        { 6, "N3" }, // Приведенная погрешность (обратный ход)
        { 7, "N3" }, // Допустимая приведенная погрешность
        { 8, "N3" }  // Вариация показаний
    };

        for (int rowIndex = 0; rowIndex < 5; rowIndex++)
        {
            var rows = await tbody.QuerySelectorAllAsync("tr");
            if (rowIndex >= rows.Length) continue;

            var row = rows[rowIndex];
            if (row == null) continue;

            for (int colIndex = 1; colIndex < 9; colIndex++)
            {
                var cell = await row.QuerySelectorAsync($"td:nth-child({colIndex + 1})");
                if (cell == null) return "Ячейка таблицы не найдена";

                var innerHtml = await cell.EvaluateFunctionAsync<string>("el => el.innerHTML");
                if (innerHtml.Trim() == "-") continue;

                double value = colIndex switch
                {
                    1 => data.PressureInputs[rowIndex],
                    2 => data.EtalonValues[rowIndex],
                    3 => data.DeviceValues[0][rowIndex],
                    4 => data.DeviceValues[1][rowIndex],
                    5 => data.ActualError[0][rowIndex],
                    6 => data.ActualError[1][rowIndex],
                    7 => data.ValidError,
                    8 => data.Variations[rowIndex],
                    _ => throw new Exception("Некорректный индекс столбца")
                };

                await cell.SetElementValueAsync(value.ToString(), columnFormats[colIndex]);
            }
        }

        return null;
    }
}
