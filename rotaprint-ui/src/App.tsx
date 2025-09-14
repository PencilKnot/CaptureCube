import React, { useState } from "react";
import { VideoPreviewModal } from "./components/VideoPreview";
import { TestGLTF } from "./TestGLTF";

export interface AdProject {
  id: string;
  name: string;
  s3ImageKeys: string[];
  status: 'downloading' | 'generating' | 'completed' | 'error';
  progress: number;
  advertisement?: {
    videoUrl: string;
    description: string;
    script?: string;
    duration?: number;
  };
  createdAt: Date;
}

export interface AdCampaign {
  id: string;
  projectId: string;
  title: string;
  description: string;
  videoUrl: string;
  script?: string;
  targetAudience?: string;
  duration?: number;
  category: string;
  createdAt: Date;
}

function App() {
  const [projects, setProjects] = useState<AdProject[]>([]);
  const [campaigns, setCampaigns] = useState<AdCampaign[]>([]);
  const [s3ImageKeys, setS3ImageKeys] = useState<string[]>([]);
  const [projectName, setProjectName] = useState('');
  const [selectedVideo, setSelectedVideo] = useState<{ url: string; title: string } | null>(null);
  const [showTestPage, setShowTestPage] = useState(false);

  const handleS3KeyInput = (keys: string[]) => {
    setS3ImageKeys(keys);
  };

  const startAdGeneration = async () => {
    if (s3ImageKeys.length === 0 || !projectName.trim()) return;

    const newProject: AdProject = {
      id: Date.now().toString(),
      name: projectName.trim(),
      s3ImageKeys: s3ImageKeys,
      status: 'downloading',
      progress: 0,
      createdAt: new Date(),
    };

    setProjects(prev => [newProject, ...prev]);

    try {
      // Call backend API to start video generation
      const response = await fetch('http://localhost:8000/api/video/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bucket: 'htn-test-bucket', // You can make this configurable later
          image_keys: s3ImageKeys,
          prompt: `Create a compelling advertisement video for ${projectName.trim()}. Show the product in an attractive and dynamic way with smooth transitions between scenes.`,
          duration: 8
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Update project with generation ID and start polling for status
      const updatedProject = { ...newProject, id: result.generation_id };
      setProjects(prev => prev.map(p => p.id === newProject.id ? updatedProject : p));

      // Start polling for generation status
      pollGenerationStatus(result.generation_id);

    } catch (error) {
      console.error('Failed to start video generation:', error);

      // Update project status to error
      setProjects(prev => prev.map(p =>
        p.id === newProject.id
          ? { ...p, status: 'error', progress: 0 }
          : p
      ));
    }

    setS3ImageKeys([]);
    setProjectName('');
  };

  const pollGenerationStatus = async (generationId: string) => {
    const pollInterval = 5000; // Poll every 5 seconds
    const maxPolls = 120; // 10 minutes maximum
    let pollCount = 0;

    const poll = async () => {
      if (pollCount >= maxPolls) {
        console.error('Polling timeout for generation:', generationId);
        setProjects(prev => prev.map(p =>
          p.id === generationId
            ? { ...p, status: 'error', progress: 0 }
            : p
        ));
        return;
      }

      try {
        const response = await fetch(`http://localhost:8000/api/video/status/${generationId}`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const statusData = await response.json();

        // Update project with current status
        setProjects(prev => prev.map(p =>
          p.id === generationId
            ? {
                ...p,
                status: statusData.status === 'completed' ? 'completed' :
                       statusData.status === 'error' ? 'error' : 'generating',
                progress: statusData.progress || 0
              }
            : p
        ));

        if (statusData.status === 'completed') {
          // Create advertisement data and campaign
          const advertisement = {
            videoUrl: `http://localhost:8000/api/video/download/${generationId}`,
            description: 'AI-generated advertisement video showcasing your product',
            script: statusData.prompt,
            duration: 8
          };

          // Update project with advertisement
          setProjects(prev => prev.map(p =>
            p.id === generationId
              ? { ...p, advertisement }
              : p
          ));

          // Create campaign
          const project = projects.find(p => p.id === generationId);
          if (project) {
            const newCampaign: AdCampaign = {
              id: Date.now().toString(),
              projectId: generationId,
              title: `${project.name} - AI Advertisement`,
              description: advertisement.description,
              videoUrl: advertisement.videoUrl,
              script: advertisement.script,
              targetAudience: 'Target Audience',
              duration: advertisement.duration,
              category: 'AI Generated',
              createdAt: new Date(),
            };

            setCampaigns(prev => [newCampaign, ...prev]);
          }

        } else if (statusData.status === 'error') {
          console.error('Video generation failed:', statusData);
        } else {
          // Continue polling
          pollCount++;
          setTimeout(poll, pollInterval);
        }

      } catch (error) {
        console.error('Error polling generation status:', error);
        pollCount++;
        setTimeout(poll, pollInterval);
      }
    };

    // Start polling
    poll();
  };


  // Show test page if requested
  if (showTestPage) {
    return <TestGLTF onBack={() => setShowTestPage(false)} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <img
                src="/logo.png"
                alt="CaptureCube Logo"
                className="h-8 w-8"
              />
              <h1 className="text-2xl font-bold text-gray-900">CaptureCube</h1>
            </div>
            <div className="flex space-x-4 items-center">
              <span className="text-sm text-gray-500">{projects.length} projects</span>
              <span className="text-sm text-gray-500">{campaigns.length} campaigns</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* S3 Input Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">New Ad Project</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Project Name
                  </label>
                  <input
                    type="text"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="Enter project name..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    S3 Image Keys
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                    <div className="space-y-2">
                      <div className="text-gray-400">
                        <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                        </svg>
                      </div>
                      <div className="text-sm text-gray-600">
                        Enter S3 keys to download product images
                      </div>
                    </div>
                    <textarea
                      placeholder="images/product1.jpg&#10;images/product2.jpg&#10;images/product3.jpg"
                      className="w-full mt-3 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      rows={4}
                      onChange={(e) => handleS3KeyInput(e.target.value.split('\n').filter(key => key.trim()))}
                    />
                  </div>
                </div>

                {s3ImageKeys.length > 0 && (
                  <div>
                    <div className="text-sm text-gray-600 mb-2">
                      {s3ImageKeys.length} S3 keys entered
                    </div>
                    <div className="max-h-32 overflow-y-auto">
                      {s3ImageKeys.map((key, index) => (
                        <div key={index} className="text-xs bg-gray-100 rounded px-2 py-1 mb-1 font-mono">
                          {key}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <button
                  onClick={startAdGeneration}
                  disabled={s3ImageKeys.length === 0 || !projectName.trim()}
                  className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Generate Advertisement
                </button>
              </div>
            </div>
          </div>

          {/* Projects List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Recent Projects</h2>
              </div>

              <div className="divide-y">
                {projects.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    No projects yet. Create your first advertisement!
                  </div>
                ) : (
                  projects.map((project) => (
                    <div key={project.id} className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{project.name}</h3>
                          <p className="text-sm text-gray-500 mt-1">
                            {project.s3ImageKeys.length} S3 images • {project.createdAt.toLocaleString()}
                          </p>

                          {/* Status and Progress */}
                          <div className="mt-3">
                            <div className="flex items-center space-x-2">
                              <StatusIcon status={project.status} />
                              <span className="text-sm capitalize text-gray-700">
                                {project.status === 'downloading' ? 'Downloading images from S3...' :
                                 project.status === 'generating' ? 'Generating advertisement video...' :
                                 project.status === 'completed' ? 'Completed' :
                                 'Error'}
                              </span>
                            </div>

                            {(project.status === 'downloading' || project.status === 'generating') && (
                              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                <div
                                  className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${project.progress}%` }}
                                />
                              </div>
                            )}
                          </div>

                          {/* Advertisement Info */}
                          {project.advertisement && (
                            <div className="mt-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
                              <h4 className="font-medium text-purple-900 mb-2">Advertisement Ready</h4>
                              <p className="text-sm text-purple-700 mb-3">{project.advertisement.description}</p>

                              <div className="grid grid-cols-1 gap-2 text-sm">
                                <div className="flex justify-between">
                                  <span className="text-purple-600">Duration:</span>
                                  <span className="font-mono text-purple-800">{project.advertisement.duration}s</span>
                                </div>
                                {project.advertisement.script && (
                                  <div className="mt-2">
                                    <span className="text-purple-600 font-medium">Script:</span>
                                    <p className="text-purple-700 text-xs mt-1 italic">{project.advertisement.script}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Campaigns Section */}
            {campaigns.length > 0 && (
              <div className="mt-8 bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b">
                  <h2 className="text-lg font-semibold text-gray-900">Generated Campaigns</h2>
                </div>

                <div className="divide-y">
                  {campaigns.map((campaign) => (
                    <div key={campaign.id} className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{campaign.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{campaign.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                            <span>Category: {campaign.category}</span>
                            <span>•</span>
                            <span>Target: {campaign.targetAudience}</span>
                            <span>•</span>
                            <span>{campaign.createdAt.toLocaleString()}</span>
                          </div>

                          {campaign.script && (
                            <div className="mt-3 p-3 bg-blue-50 rounded border border-blue-200">
                              <div className="text-xs font-medium text-blue-700 mb-2">ADVERTISEMENT SCRIPT</div>
                              <p className="text-sm text-blue-800 italic">{campaign.script}</p>
                              <div className="flex justify-between items-center mt-2 text-xs text-blue-600">
                                <span>Duration: {campaign.duration}s</span>
                                <span className="bg-blue-100 px-2 py-1 rounded">Ready for Review</span>
                              </div>
                            </div>
                          )}
                        </div>

                        <button
                          onClick={() => setSelectedVideo({ url: campaign.videoUrl, title: campaign.title })}
                          className="ml-4 bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700 transition-colors"
                        >
                          Preview Video
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Video Preview Modal */}
      <VideoPreviewModal
        isOpen={selectedVideo !== null}
        onClose={() => setSelectedVideo(null)}
        videoUrl={selectedVideo?.url || ''}
        title={selectedVideo?.title || ''}
      />
    </div>
  );
}

function StatusIcon({ status }: { status: AdProject['status'] }) {
  switch (status) {
    case 'downloading':
      return <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />;
    case 'generating':
      return <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />;
    case 'completed':
      return <div className="w-4 h-4 bg-green-600 rounded-full flex items-center justify-center">
        <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      </div>;
    case 'error':
      return <div className="w-4 h-4 bg-red-600 rounded-full flex items-center justify-center">
        <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </div>;
  }
}

export default App;

