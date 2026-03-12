import { useState, useEffect, useMemo } from 'react'
import Sidebar from './components/Sidebar'
import TrackTable from './components/TrackTable'
import Player from './components/Player'
import { parseCSV } from './utils/csv'

export default function App() {
  const [spotifyTracks, setSpotifyTracks] = useState([])
  const [soundcloudTracks, setSoundcloudTracks] = useState([])
  const [source, setSource] = useState('spotify')
  const [selectedPlaylist, setSelectedPlaylist] = useState('All')
  const [search, setSearch] = useState('')
  const [currentTrack, setCurrentTrack] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadData() {
      try {
        const [spotifyRes, soundcloudRes] = await Promise.all([
          fetch('/data/spotify.csv'),
          fetch('/data/soundcloud.csv'),
        ])
        if (!spotifyRes.ok || !soundcloudRes.ok) throw new Error('CSV files not found in public/data/')
        const [spotifyText, soundcloudText] = await Promise.all([
          spotifyRes.text(),
          soundcloudRes.text(),
        ])
        setSpotifyTracks(parseCSV(spotifyText))
        setSoundcloudTracks(parseCSV(soundcloudText))
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const tracks = source === 'spotify' ? spotifyTracks : soundcloudTracks

  const playlists = useMemo(() => {
    const names = [...new Set(tracks.map(t => t.name_of_playlist).filter(Boolean))]
    return ['All', ...names]
  }, [tracks])

  const filteredTracks = useMemo(() => {
    return tracks
      .filter(t => selectedPlaylist === 'All' || t.name_of_playlist === selectedPlaylist)
      .filter(t => {
        if (!search) return true
        const q = search.toLowerCase()
        return (
          t.trackname?.toLowerCase().includes(q) ||
          t.artists?.toLowerCase().includes(q)
        )
      })
  }, [tracks, selectedPlaylist, search])

  function handleSourceChange(newSource) {
    setSource(newSource)
    setSelectedPlaylist('All')
    setSearch('')
    setCurrentTrack(null)
  }

  function handlePlaylistSelect(pl) {
    setSelectedPlaylist(pl)
    setSearch('')
  }

  return (
    <div className={`app ${currentTrack ? 'has-player' : ''}`}>
      <Sidebar
        source={source}
        playlists={playlists}
        selectedPlaylist={selectedPlaylist}
        tracks={tracks}
        onSourceChange={handleSourceChange}
        onPlaylistSelect={handlePlaylistSelect}
      />
      <main className="main">
        {loading && <div className="state-msg">Loading playlists...</div>}
        {error && <div className="state-msg error">Error: {error}<br /><small>Run <code>scripts/export_for_web.py</code> to generate the CSV files.</small></div>}
        {!loading && !error && (
          <TrackTable
            tracks={filteredTracks}
            source={source}
            search={search}
            selectedPlaylist={selectedPlaylist}
            onSearch={setSearch}
            onPlay={setCurrentTrack}
            currentTrack={currentTrack}
          />
        )}
      </main>
      {currentTrack && (
        <Player
          track={currentTrack}
          tracks={filteredTracks}
          onPlay={setCurrentTrack}
          onClose={() => setCurrentTrack(null)}
        />
      )}
    </div>
  )
}
