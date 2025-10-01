using PuppeteerSharp;

namespace Infrastructure.DocumentProcessor.Creator;

internal class HTMLCreationResult
{
    public IPage? HTMLPage { get; init; }
    public string? Error { get; init; }

    private HTMLCreationResult() { }

    public static HTMLCreationResult Success(IPage htmlPage) => new() { HTMLPage = htmlPage };
    public static HTMLCreationResult Failure(string error) => new() { Error = error };
}
