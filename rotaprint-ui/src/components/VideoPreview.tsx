import React from 'react';

interface VideoPreviewProps {
  videoUrl: string;
  className?: string;
}

export function VideoPreview({ videoUrl, className = '' }: VideoPreviewProps) {
  const [isLoading, setIsLoading] = React.useState(true);
  const [hasError, setHasError] = React.useState(false);

  const handleLoadStart = () => {
    setIsLoading(true);
    setHasError(false);
  };

  const handleCanPlay = () => {
    setIsLoading(false);
  };

  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  return (
    <div className="relative">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Loading video...</p>
          </div>
        </div>
      )}

      {hasError ? (
        <div className="flex items-center justify-center bg-gray-100 rounded p-8">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="mt-2 text-sm text-gray-600">Failed to load video</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 text-purple-600 hover:text-purple-700 text-sm underline"
            >
              Try again
            </button>
          </div>
        </div>
      ) : (
        <video
          controls
          className={`w-full h-full object-contain ${className}`}
          src={videoUrl}
          onLoadStart={handleLoadStart}
          onCanPlay={handleCanPlay}
          onError={handleError}
          preload="metadata"
        >
          Your browser does not support the video tag.
        </video>
      )}
    </div>
  );
}

// Modal component for full-screen video viewing
export function VideoPreviewModal({
  isOpen,
  onClose,
  videoUrl,
  title
}: {
  isOpen: boolean;
  onClose: () => void;
  videoUrl: string;
  title: string;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-75 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-6xl h-[80vh]">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Video Player */}
          <div className="p-6 h-full flex items-center justify-center bg-black rounded-b-lg">
            <VideoPreview
              videoUrl={videoUrl}
              className="max-w-full max-h-full rounded"
            />
          </div>
        </div>
      </div>
    </div>
  );
}