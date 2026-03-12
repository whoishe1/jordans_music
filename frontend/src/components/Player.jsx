import { useState, useEffect, useRef } from 'react'

export default function Player({ track, tracks, onPlay, onClose }) {
  const [shuffle, setShuffle] = useState(false)

  const currentIndex = tracks.findIndex(t => t.track_id === track.track_id)

  // Keep a ref of latest state so callbacks don't close over stale values
  const stateRef = useRef({ shuffle, currentIndex, tracks, onPlay })
  useEffect(() => { stateRef.current = { shuffle, currentIndex, tracks, onPlay } })

  const controllerRef = useRef(null)
  const controllerReadyRef = useRef(false)
  const embedDivRef = useRef(null)
  const wasPlayingRef = useRef(false)

  function handleNext() {
    const { shuffle, currentIndex, tracks, onPlay } = stateRef.current
    if (shuffle) {
      let nextIndex
      do { nextIndex = Math.floor(Math.random() * tracks.length) }
      while (tracks.length > 1 && nextIndex === currentIndex)
      onPlay(tracks[nextIndex])
    } else {
      if (currentIndex >= tracks.length - 1) return
      onPlay(tracks[currentIndex + 1])
    }
  }

  function handlePrev() {
    const { currentIndex, tracks, onPlay } = stateRef.current
    if (currentIndex <= 0) return
    onPlay(tracks[currentIndex - 1])
  }

  const handleNextRef = useRef(handleNext)
  useEffect(() => { handleNextRef.current = handleNext })

  // Load Spotify IFrame API once on mount
  useEffect(() => {
    function createController() {
      window.SpotifyIFrameAPI.createController(
        embedDivRef.current,
        { uri: `spotify:track:${track.track_id}`, height: '80' },
        (controller) => {
          controllerRef.current = controller
          controllerReadyRef.current = true
          controller.play()

          controller.addListener('playback_update', (e) => {
            const { isPaused, position } = e?.data ?? e
            console.log('[IFrame API]', { isPaused, position, wasPlaying: wasPlayingRef.current })
            if (!isPaused && position > 0) wasPlayingRef.current = true
            if (isPaused && position === 0 && wasPlayingRef.current) {
              wasPlayingRef.current = false
              handleNextRef.current()
            }
          })
        }
      )
    }

    if (window.SpotifyIFrameAPI) {
      createController()
    } else {
      const scriptId = 'spotify-iframe-api'
      if (!document.getElementById(scriptId)) {
        const script = document.createElement('script')
        script.id = scriptId
        script.src = 'https://open.spotify.com/embed/iframe-api/v1'
        script.async = true
        document.body.appendChild(script)
      }
      window.onSpotifyIframeApiReady = (IFrameAPI) => {
        window.SpotifyIFrameAPI = IFrameAPI
        createController()
      }
    }

    return () => {
      controllerRef.current?.destroy?.()
      controllerRef.current = null
      controllerReadyRef.current = false
    }
  }, [])

  // When track changes, swap URI and play
  useEffect(() => {
    if (!controllerReadyRef.current || !controllerRef.current) return
    wasPlayingRef.current = false
    controllerRef.current.loadUri(`spotify:track:${track.track_id}`)
    controllerRef.current.play()
  }, [track.track_id])

  return (
    <div className="player">
      <div className="player-top">
        <div className="player-info">
          <div className="player-track">{track.trackname}</div>
          <div className="player-artist">{track.artists}</div>
        </div>

        <div className="player-controls">
          <button
            className={`ctrl-btn ${shuffle ? 'active' : ''}`}
            onClick={() => setShuffle(s => !s)}
            title="Shuffle"
          >
            ⇌
          </button>
          <button
            className="ctrl-btn"
            onClick={handlePrev}
            disabled={currentIndex <= 0}
            title="Previous"
          >
            ⏮
          </button>
          <button
            className="ctrl-btn"
            onClick={handleNext}
            disabled={!shuffle && currentIndex >= tracks.length - 1}
            title="Next"
          >
            ⏭
          </button>
        </div>

        <div className="player-actions">
          <button className="player-close" onClick={onClose} title="Close">✕</button>
        </div>
      </div>

      <div className="embed-widget-container">
        <div ref={embedDivRef} />
      </div>
    </div>
  )
}
