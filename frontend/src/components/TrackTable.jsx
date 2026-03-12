import { downloadCSV } from '../utils/csv'

export default function TrackTable({ tracks, source, search, selectedPlaylist, onSearch, onPlay, currentTrack }) {
  const isSpotify = source === 'spotify'
  const label = selectedPlaylist === 'All' ? 'All Tracks' : selectedPlaylist
  const filename = `${source}_${selectedPlaylist.replace(/\s+/g, '_').toLowerCase()}.csv`

  return (
    <div className="track-table-wrap">
      <div className="table-header">
        <div className="table-title">
          <h2>{label}</h2>
          <span className="track-count">{tracks.length} tracks</span>
        </div>
        <div className="table-actions">
          <input
            className="search-input"
            type="text"
            placeholder="Search tracks or artists..."
            value={search}
            onChange={e => onSearch(e.target.value)}
          />
          <button
            className="btn-download"
            onClick={() => downloadCSV(tracks, filename)}
            disabled={!tracks.length}
          >
            ↓ Download CSV
          </button>
        </div>
      </div>

      {tracks.length === 0 ? (
        <div className="state-msg">No tracks found.</div>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Artist</th>
                <th>Track</th>
                {isSpotify && <th>Album</th>}
                {selectedPlaylist === 'All' && <th>Playlist</th>}
                {isSpotify && <th></th>}
              </tr>
            </thead>
            <tbody>
              {tracks.map((track, i) => {
                const isPlaying = currentTrack?.track_id === track.track_id
                return (
                  <tr key={`${track.track_id || i}-${i}`} className={isPlaying ? 'playing' : ''}>
                    <td className="row-num">{isPlaying ? '▶' : i + 1}</td>
                    <td className="cell-artist">{track.artists}</td>
                    <td className="cell-track">{track.trackname}</td>
                    {isSpotify && <td className="cell-album">{track.album}</td>}
                    {selectedPlaylist === 'All' && (
                      <td><span className="pill">{track.name_of_playlist}</span></td>
                    )}
                    {isSpotify && (
                      <td>
                        <button
                          className={`play-btn ${isPlaying ? 'playing' : ''}`}
                          onClick={() => onPlay(isPlaying ? null : track)}
                          title={isPlaying ? 'Stop' : 'Play on Spotify'}
                        >
                          {isPlaying ? '■' : '▶'}
                        </button>
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
