using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Unicode;
using Windows.Media.Control;
using WindowsMediaController;
using static WindowsMediaController.MediaManager;

namespace SMTC_NowPlaying;

internal class Program
{
    static MediaManager? mediaManager;
    static MediaSession? mediaSession;
    static GlobalSystemMediaTransportControlsSessionMediaProperties? sessionInfo;

    /// <summary>
    /// 曲情報を格納するクラス
    /// </summary>
    /// 
    public class DictInfo
    {
        // Title (曲名)
        [JsonPropertyName("Title")]
        public string? Title { get; set; }

        // Subtitle (サブタイトル)
        [JsonPropertyName("Subtitle")]
        public string? Subtitle { get; set; }

        // Artist (アーティスト)
        [JsonPropertyName("Artist")]
        public string? Artist { get; set; }

        // AlbumArtist (アルバムアーティスト)
        [JsonPropertyName("AlbumArtist")]
        public string? AlbumArtist { get; set; }

        // AlbumTitle (アルバム名)
        [JsonPropertyName("AlbumTitle")]
        public string? AlbumTitle { get; set; }

        // TrackNumber (トラック番号)
        [JsonPropertyName("TrackNumber")]
        public int? TrackNumber { get; set; }

        // AlbumTrackCount (アルバム内のトラック数)
        [JsonPropertyName("AlbumTrackCount")]
        public int? AlbumTrackCount { get; set; }

        // Genres (ジャンル)
        [JsonPropertyName("Genres")]
        public IReadOnlyList<string>? Genres { get; set; }

        // Thumbnail (サムネイル)
        [JsonPropertyName("Thumbnail")]
        public Windows.Storage.Streams.IRandomAccessStreamReference? Thumbnail { get; set; }

        // PlaybackType (再生タイプ)
        [JsonPropertyName("PlaybackType")]
        public Windows.Media.MediaPlaybackType? PlaybackType { get; set; }

        // Id (内部ID)
        [JsonPropertyName("Id")]
        public string? Id { get; set; }
    }

    /// <summary>
    /// JsonSerializerOptionsの設定
    /// </summary>
    /// 
    private static readonly JsonSerializerOptions options = new()
    {
        Encoder = JavaScriptEncoder.Create(UnicodeRanges.All),
        WriteIndented = true
    };

    /// <summary>
    /// 入力をJSON文字列に変換する
    /// </summary>
    /// <param name="obj">定義済みのクラスオブジェクト</param>
    /// <returns>JSON文字列 (入力が異常な場合はnull)</returns>
    /// 
    public static string? ToJson(Object obj)
    {
        try
        {
            var json = JsonSerializer.Serialize(obj, options);
            return json;
        }
        catch (JsonException e)
        {
            Console.WriteLine(e.Message);
            return null;
        }
    }

    async static Task Main(string[] args)
    {
        mediaManager = new MediaManager();
        mediaManager.Start();

        mediaSession = mediaManager.GetFocusedSession();
        sessionInfo = await mediaSession.ControlSession.TryGetMediaPropertiesAsync();
        var songInfo = new DictInfo
        {
            Title = sessionInfo.Title,
            Subtitle = sessionInfo.Subtitle,
            Artist = sessionInfo.Artist,
            AlbumArtist = sessionInfo.AlbumArtist,
            AlbumTitle = sessionInfo.AlbumTitle,
            TrackNumber = sessionInfo.TrackNumber,
            AlbumTrackCount = sessionInfo.AlbumTrackCount,
            Genres = sessionInfo.Genres,
            Thumbnail = sessionInfo.Thumbnail,
            PlaybackType = sessionInfo.PlaybackType,
            Id = mediaSession.Id
        };

        Console.WriteLine(ToJson(songInfo));

    }
}

