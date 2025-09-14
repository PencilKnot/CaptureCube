import React from 'react';
import { VideoPreview } from './VideoPreview';

interface VideoPreviewPageProps {
  videoUrl: string;
  title: string;
  onBack: () => void;
}

export function VideoPreviewPage({ videoUrl, title, onBack }: VideoPreviewPageProps) {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="text-gray-300 hover:text-white transition-colors p-2 rounded-md hover:bg-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div className="flex items-center space-x-3">
                <img
                  src="/logo.png"
                  alt="CaptureCube Logo"
                  className="h-6 w-6"
                />
                <h1 className="text-xl font-bold text-white">CaptureCube</h1>
              </div>
            </div>
            <h2 className="text-lg font-medium text-gray-200 truncate max-w-md">{title}</h2>
          </div>
        </div>
      </header>

      {/* Video Content */}
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-80px)] p-4">
        <div className="w-full max-w-6xl">
          {/* Video Player Container */}
          <div className="bg-black rounded-lg shadow-2xl overflow-hidden">
            <div className="aspect-video">
              <VideoPreview
                videoUrl={videoUrl}
                className="w-full h-full rounded-lg"
              />
            </div>
          </div>

          {/* Video Info */}
          <div className="mt-6 text-center">
            <h3 className="text-2xl font-bold text-white mb-2">{title}</h3>
            <p className="text-gray-400 text-sm">
              AI-generated advertisement • 8 seconds • HD Quality
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center space-x-4 mt-6">
            <button
              onClick={onBack}
              className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors font-medium"
            >
              ← Back to Projects
            </button>

            <a
              href={videoUrl.replace('/stream/', '/download/')}
              download
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors font-medium inline-block"
            >
              Download Video
            </a>

            <button
              onClick={() => {
                if (navigator.share) {
                  navigator.share({
                    title: title,
                    text: 'Check out this AI-generated advertisement!',
                    url: window.location.href
                  });
                } else {
                  navigator.clipboard.writeText(window.location.href);
                  alert('Video link copied to clipboard!');
                }
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
            >
              Share Video
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}