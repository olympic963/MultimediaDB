import React, { useEffect, useRef, useState } from 'react';
import { Search, Play, Pause, RotateCcw, Home } from 'lucide-react';
import WaveSurfer from 'wavesurfer.js';

// Sample audio data with reliable audio sources
const sampleResults = [
  {
    id: 1,
    title: "Guitar Acoustic",
    artist: "AudioCue",
    duration: "3:45",
    url: "https://assets.mixkit.co/music/preview/mixkit-guitar-acoustic-opener-2291.mp3"
  },
  {
    id: 2,
    title: "Serene View",
    artist: "MixKit",
    duration: "4:20",
    url: "https://assets.mixkit.co/music/preview/mixkit-serene-view-443.mp3"
  },
  {
    id: 3,
    title: "Tech House",
    artist: "MixKit",
    duration: "5:15",
    url: "https://assets.mixkit.co/music/preview/mixkit-tech-house-vibes-130.mp3"
  }
];

const AudioPlayer = ({ url, title }) => {
  const waveformRef = useRef(null);
  const wavesurfer = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState("0:00");
  const [duration, setDuration] = useState("0:00");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isComponentMounted = true;
    const abortController = new AbortController();

    const initializeWaveSurfer = async () => {
      try {
        if (waveformRef.current && isComponentMounted) {
          if (wavesurfer.current) {
            wavesurfer.current.destroy();
          }

          wavesurfer.current = WaveSurfer.create({
            container: waveformRef.current,
            waveColor: '#4F46E5',
            progressColor: '#818CF8',
            cursorColor: '#4F46E5',
            barWidth: 2,
            barRadius: 3,
            cursorWidth: 1,
            height: 80,
            barGap: 3,
            mediaControls: true,
            normalize: true,
            fetchParams: {
              signal: abortController.signal,
              cache: 'force-cache'
            }
          });

          wavesurfer.current.on('ready', () => {
            if (isComponentMounted && wavesurfer.current) {
              const audioDuration = wavesurfer.current.getDuration();
              setDuration(formatTime(audioDuration));
              setError(null);
              setIsLoading(false);
            }
          });

          wavesurfer.current.on('audioprocess', () => {
            if (isComponentMounted && wavesurfer.current) {
              const currentTime = wavesurfer.current.getCurrentTime();
              setCurrentTime(formatTime(currentTime));
            }
          });

          wavesurfer.current.on('error', (err) => {
            if (isComponentMounted) {
              console.error('WaveSurfer error:', err);
              setError('Failed to load audio file. Please try again later.');
              setIsLoading(false);
            }
          });

          try {
            const response = await fetch(url, { 
              method: 'HEAD',
              signal: abortController.signal
            });
            
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            await wavesurfer.current.load(url);
          } catch (loadError) {
            if (isComponentMounted) {
              console.error('Error loading audio:', loadError);
              setError('Unable to load audio file. Please check your connection and try again.');
              setIsLoading(false);
            }
          }
        }
      } catch (err) {
        if (isComponentMounted) {
          console.error('Error initializing WaveSurfer:', err);
          setError('Failed to initialize audio player. Please refresh the page.');
          setIsLoading(false);
        }
      }
    };

    initializeWaveSurfer();

    return () => {
      isComponentMounted = false;
      abortController.abort();
      if (wavesurfer.current) {
        wavesurfer.current.destroy();
      }
    };
  }, [url]);

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handlePlayPause = () => {
    if (wavesurfer.current && !error) {
      wavesurfer.current.playPause();
      setIsPlaying(!isPlaying);
    }
  };

  const handleRestart = () => {
    if (wavesurfer.current && !error) {
      wavesurfer.current.stop();
      wavesurfer.current.play();
      setIsPlaying(true);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h3 className="text-xl font-semibold mb-4">{title}</h3>
      {isLoading ? (
        <div className="flex items-center justify-center h-20 bg-gray-50 rounded-md">
          <div className="animate-pulse text-gray-500">Loading audio...</div>
        </div>
      ) : error ? (
        <div className="text-red-500 p-4 bg-red-50 rounded-md mb-4">{error}</div>
      ) : (
        <>
          <div ref={waveformRef} className="mb-4" />
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={handlePlayPause}
                className="p-2 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!!error}
              >
                {isPlaying ? <Pause size={20} /> : <Play size={20} />}
              </button>
              <button
                onClick={handleRestart}
                className="p-2 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!!error}
              >
                <RotateCcw size={20} />
              </button>
            </div>
            <div className="text-sm text-gray-600">
              {currentTime} / {duration}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

const ResultsPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="flex items-center gap-4 mb-8">
          <div className="text-gray-600">
            <Home size={24} />
          </div>
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              className="w-full pl-10 pr-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:border-blue-500"
              placeholder="Search for audio..."
              readOnly
            />
          </div>
        </div>

        <div className="space-y-6">
          {sampleResults.map((result) => (
            <AudioPlayer key={result.id} url={result.url} title={`${result.title} - ${result.artist}`} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
