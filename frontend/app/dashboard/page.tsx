'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, Candidate, QueueMetrics } from '@/lib/api';
import CandidateModal from './CandidateModal';

type MetricFilter = 'all' | 'queue' | 'retry' | 'processed';

export default function Dashboard() {
  const router = useRouter();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [filteredCandidates, setFilteredCandidates] = useState<Candidate[]>([]);
  const [metrics, setMetrics] = useState<QueueMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [metricFilter, setMetricFilter] = useState<MetricFilter>('all');
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);

  // Form state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [skills, setSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState('');
  const [profileLinks, setProfileLinks] = useState<Record<string, string>>({});
  const [newLinkKey, setNewLinkKey] = useState('');
  const [newLinkValue, setNewLinkValue] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [uploadingResumeFor, setUploadingResumeFor] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    // Refresh every 5 seconds
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Filter candidates based on metric selection
    // Note: This is a simplified filter. In a real app, you'd need backend support
    // to properly track which candidates are in which queue state
    setFilteredCandidates(candidates);
  }, [candidates, metricFilter]);

  const loadData = async () => {
    try {
      const [candidatesData, metricsData] = await Promise.all([
        apiClient.getCandidates(),
        apiClient.getQueueMetrics(),
      ]);
      setCandidates(candidatesData);
      setMetrics(metricsData);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load data:', err);
      // If unauthorized, redirect to login
      if (err instanceof Error && err.message.includes('401')) {
        router.push('/');
      }
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setUploading(true);

    try {
      // Step 1: Create candidate
      const candidate = await apiClient.createCandidate({
        full_name: fullName,
        email: email,
        phone: phone || undefined,
        skills: skills.length > 0 ? skills : undefined,
        profile_links: Object.keys(profileLinks).length > 0 ? profileLinks : undefined,
      });

      // Step 2: Upload resume if provided
      if (resumeFile) {
        await apiClient.uploadResume(candidate.id, resumeFile);
      }

      // Reset form
      setFullName('');
      setEmail('');
      setPhone('');
      setSkills([]);
      setSkillInput('');
      setProfileLinks({});
      setNewLinkKey('');
      setNewLinkValue('');
      setResumeFile(null);
      setShowUploadForm(false);

      // Reload data
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create candidate');
    } finally {
      setUploading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    router.push('/');
  };

  const handleResumeUpload = async (candidateId: string, file: File) => {
    setUploadingResumeFor(candidateId);
    try {
      await apiClient.uploadResume(candidateId, file);
      alert('Resume uploaded successfully! Processing will start shortly.');
      loadData();
    } catch (err) {
      alert('Failed to upload resume: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setUploadingResumeFor(null);
    }
  };

  const handleAddSkill = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && skillInput.trim()) {
      e.preventDefault();
      if (!skills.includes(skillInput.trim())) {
        setSkills([...skills, skillInput.trim()]);
      }
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setSkills(skills.filter(skill => skill !== skillToRemove));
  };

  const handleAddLink = () => {
    if (newLinkKey.trim() && newLinkValue.trim()) {
      setProfileLinks({ ...profileLinks, [newLinkKey.trim()]: newLinkValue.trim() });
      setNewLinkKey('');
      setNewLinkValue('');
    }
  };

  const handleRemoveLink = (key: string) => {
    const newLinks = { ...profileLinks };
    delete newLinks[key];
    setProfileLinks(newLinks);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Candidate Hiring Dashboard</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Metrics */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <button
              onClick={() => setMetricFilter('all')}
              className={`bg-white p-6 rounded-lg shadow text-left hover:shadow-lg transition-shadow ${
                metricFilter === 'all' ? 'ring-2 ring-indigo-600' : ''
              }`}
            >
              <div className="text-sm font-medium text-gray-600">Total Candidates</div>
              <div className="text-3xl font-bold text-gray-900 mt-2">{candidates.length}</div>
            </button>
            <button
              onClick={() => setMetricFilter('queue')}
              className={`bg-white p-6 rounded-lg shadow text-left hover:shadow-lg transition-shadow ${
                metricFilter === 'queue' ? 'ring-2 ring-indigo-600' : ''
              }`}
            >
              <div className="text-sm font-medium text-gray-600">Queue Length</div>
              <div className="text-3xl font-bold text-indigo-600 mt-2">{metrics.queue_length}</div>
            </button>
            <button
              onClick={() => setMetricFilter('retry')}
              className={`bg-white p-6 rounded-lg shadow text-left hover:shadow-lg transition-shadow ${
                metricFilter === 'retry' ? 'ring-2 ring-indigo-600' : ''
              }`}
            >
              <div className="text-sm font-medium text-gray-600">Retry Queue</div>
              <div className="text-3xl font-bold text-yellow-600 mt-2">{metrics.retry_queue_length}</div>
            </button>
            <button
              onClick={() => setMetricFilter('processed')}
              className={`bg-white p-6 rounded-lg shadow text-left hover:shadow-lg transition-shadow ${
                metricFilter === 'processed' ? 'ring-2 ring-indigo-600' : ''
              }`}
            >
              <div className="text-sm font-medium text-gray-600">Processed</div>
              <div className="text-3xl font-bold text-green-600 mt-2">{metrics.processed_count || 0}</div>
            </button>
          </div>
        )}

        {/* Add Candidate Button */}
        <div className="mb-6">
          <button
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            {showUploadForm ? 'Cancel' : '+ Add Candidate'}
          </button>
        </div>

        {/* Upload Form */}
        {showUploadForm && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-xl font-semibold mb-4">Add New Candidate</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Skills (press Enter to add)
                  </label>
                  <div className="w-full px-3 py-2 border border-gray-300 rounded-md focus-within:ring-indigo-500 focus-within:border-indigo-500">
                    <div className="flex flex-wrap gap-2 mb-2">
                      {skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center gap-1 px-2 py-1 bg-indigo-100 text-indigo-800 text-sm rounded"
                        >
                          {skill}
                          <button
                            type="button"
                            onClick={() => handleRemoveSkill(skill)}
                            className="text-indigo-600 hover:text-indigo-800 font-bold"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                    <input
                      type="text"
                      value={skillInput}
                      onChange={(e) => setSkillInput(e.target.value)}
                      onKeyDown={handleAddSkill}
                      placeholder={skills.length === 0 ? "Type a skill and press Enter" : "Add another skill..."}
                      className="w-full outline-none border-none focus:ring-0 p-0 text-black"
                    />
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Profile Links
                </label>
                <div className="w-full px-3 py-2 border border-gray-300 rounded-md space-y-2">
                  {Object.entries(profileLinks).map(([key, value]) => (
                    <div key={key} className="flex items-center gap-2 bg-gray-50 p-2 rounded">
                      <span className="text-sm font-medium text-gray-700 capitalize">{key}:</span>
                      <span className="text-sm text-gray-600 flex-1 truncate">{value}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveLink(key)}
                        className="text-red-600 hover:text-red-800 font-bold"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newLinkKey}
                      onChange={(e) => setNewLinkKey(e.target.value)}
                      placeholder="Platform (e.g., LinkedIn)"
                      className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm text-black"
                    />
                    <input
                      type="url"
                      value={newLinkValue}
                      onChange={(e) => setNewLinkValue(e.target.value)}
                      placeholder="URL"
                      className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm text-black"
                    />
                    <button
                      type="button"
                      onClick={handleAddLink}
                      className="px-3 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Resume (PDF)
                </label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-black"
                />
              </div>
              {error && (
                <div className="text-red-600 text-sm">{error}</div>
              )}
              <button
                type="submit"
                disabled={uploading}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {uploading ? 'Uploading...' : 'Add Candidate'}
              </button>
            </form>
          </div>
        )}

        {/* Candidates Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">
              Candidates ({filteredCandidates.length})
              {metricFilter !== 'all' && (
                <span className="text-sm font-normal text-gray-500 ml-2">
                  - Filtered by {metricFilter}
                </span>
              )}
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Phone
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Skills
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCandidates.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                      No candidates yet. Add your first candidate above!
                    </td>
                  </tr>
                ) : (
                  filteredCandidates.map((candidate) => (
                    <tr key={candidate.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        <button
                          onClick={() => setSelectedCandidateId(candidate.id)}
                          className="text-indigo-600 hover:text-indigo-900 hover:underline"
                        >
                          {candidate.full_name}
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {candidate.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {candidate.phone || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {candidate.skills && candidate.skills.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {candidate.skills.map((skill, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <label
                          className={`cursor-pointer px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-xs ${
                            uploadingResumeFor === candidate.id ? 'opacity-50 cursor-not-allowed' : ''
                          }`}
                        >
                          {uploadingResumeFor === candidate.id ? 'Uploading...' : '📤 Upload Resume'}
                          <input
                            type="file"
                            accept=".pdf"
                            className="hidden"
                            disabled={uploadingResumeFor === candidate.id}
                            onChange={(e) => {
                              const file = e.target.files?.[0];
                              if (file) {
                                handleResumeUpload(candidate.id, file);
                              }
                            }}
                          />
                        </label>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Candidate Detail Modal */}
      {selectedCandidateId && (
        <CandidateModal
          candidateId={selectedCandidateId}
          onClose={() => setSelectedCandidateId(null)}
          onUpdate={loadData}
        />
      )}
    </div>
  );
}
