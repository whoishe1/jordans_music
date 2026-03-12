export default function Sidebar({ source, playlists, selectedPlaylist, tracks, onSourceChange, onPlaylistSelect }) {
  const countFor = (pl) =>
    pl === 'All' ? tracks.length : tracks.filter(t => t.name_of_playlist === pl).length

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="logo">♪</span>
        <h1>Jordan's Music</h1>
      </div>

      <div className="source-toggle">
        <button
          className={`source-btn ${source === 'spotify' ? 'active spotify' : ''}`}
          onClick={() => onSourceChange('spotify')}
        >
          Spotify
        </button>
        <button
          className={`source-btn ${source === 'soundcloud' ? 'active soundcloud' : ''}`}
          onClick={() => onSourceChange('soundcloud')}
        >
          SoundCloud
        </button>
      </div>

      <nav className="playlist-nav">
        <p className="nav-label">Playlists</p>
        {playlists.map(pl => (
          <button
            key={pl}
            className={`playlist-item ${selectedPlaylist === pl ? 'active' : ''}`}
            onClick={() => onPlaylistSelect(pl)}
          >
            <span className="playlist-name">{pl}</span>
            <span className="playlist-count">{countFor(pl)}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
