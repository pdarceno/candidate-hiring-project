'use client';

import { useState, useEffect } from 'react';
import { apiClient, Candidate, Application, ApplicationStatus } from '@/lib/api';

interface CandidateModalProps {
  candidateId: string;
  onClose: () => void;
  onUpdate: () => void;
}

export default function CandidateModal({ candidateId, onClose, onUpdate }: CandidateModalProps) {
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  
  // Edit form state
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [skills, setSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState('');
  const [profileLinks, setProfileLinks] = useState<Record<string, string>>({});
  const [newLinkKey, setNewLinkKey] = useState('');
  const [newLinkValue, setNewLinkValue] = useState('');
  
  // Application form state
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [jobTitle, setJobTitle] = useState('');
  
  useEffect(() => {
    loadData();
  }, [candidateId]);

  const loadData = async () => {
    try {
      const [candidateData, applicationsData] = await Promise.all([
        apiClient.getCandidate(candidateId),
        apiClient.getApplicationsForCandidate(candidateId),
      ]);
      setCandidate(candidateData);
      setApplications(applicationsData);
      setFullName(candidateData.full_name);
      setPhone(candidateData.phone || '');
      setSkills(candidateData.skills || []);
      setProfileLinks(candidateData.profile_links || {});
      setLoading(false);
    } catch (err) {
      console.error('Failed to load candidate:', err);
      setLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!candidate) return;
    try {
      await apiClient.updateCandidate(candidate.id, {
        full_name: fullName,
        phone: phone || undefined,
        skills: skills.length > 0 ? skills : undefined,
        profile_links: Object.keys(profileLinks).length > 0 ? profileLinks : undefined,
      });
      setEditing(false);
      loadData();
      onUpdate();
    } catch (err) {
      alert('Failed to update candidate');
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

  const handleApplyToJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidate) return;
    try {
      await apiClient.createApplication({
        candidate_id: candidate.id,
        job_title: jobTitle,
        status: ApplicationStatus.APPLIED,
      });
      setJobTitle('');
      setShowApplicationForm(false);
      loadData();
    } catch (err) {
      alert('Failed to create application');
    }
  };

  const handleStatusChange = async (applicationId: string, newStatus: ApplicationStatus) => {
    try {
      await apiClient.updateApplicationStatus(applicationId, newStatus);
      loadData();
    } catch (err) {
      alert('Failed to update status');
    }
  };

  const handleResumeUpload = async (file: File) => {
    if (!candidate) return;
    try {
      await apiClient.uploadResume(candidate.id, file);
      alert('Resume uploaded successfully!');
      onUpdate();
    } catch (err) {
      alert('Failed to upload resume');
    }
  };

  const handleEnrichProfile = async (file: File) => {
    if (!candidate) return;
    try {
      await apiClient.enrichProfile(candidate.id, file);
      alert('Profile enrichment started!');
      onUpdate();
    } catch (err) {
      alert('Failed to enrich profile');
    }
  };

  const getStatusColor = (status: ApplicationStatus) => {
    switch (status) {
      case ApplicationStatus.APPLIED:
        return 'bg-blue-100 text-blue-800';
      case ApplicationStatus.INTERVIEWING:
        return 'bg-yellow-100 text-yellow-800';
      case ApplicationStatus.HIRED:
        return 'bg-green-100 text-green-800';
      case ApplicationStatus.REJECTED:
        return 'bg-red-100 text-red-800';
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="text-lg">Loading...</div>
        </div>
      </div>
    );
  }

  if (!candidate) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Candidate Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Candidate Info */}
          <div className="bg-gray-50 p-4 rounded-lg">
            {!editing ? (
              <>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold">{candidate.full_name}</h3>
                    <p className="text-gray-600">{candidate.email}</p>
                    {candidate.phone && <p className="text-gray-600">{candidate.phone}</p>}
                  </div>
                  <button
                    onClick={() => setEditing(true)}
                    className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  >
                    Edit
                  </button>
                </div>
                {candidate.skills && candidate.skills.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {candidate.skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-indigo-100 text-indigo-800 text-sm rounded"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                )}
                {candidate.profile_links && Object.keys(candidate.profile_links).length > 0 && (
                  <div className="mt-4 space-y-2">
                    <h4 className="text-sm font-medium text-gray-700">Profile Links</h4>
                    {Object.entries(candidate.profile_links).map(([key, value]) => (
                      <div key={key} className="flex items-center gap-2">
                        <span className="text-sm text-gray-600 capitalize">{key}:</span>
                        <a
                          href={value}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-indigo-600 hover:underline"
                        >
                          {value}
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-black"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-black"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Skills (press Enter to add)
                  </label>
                  <div className="w-full px-3 py-2 border border-gray-300 rounded-md">
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
                      placeholder="Add skill..."
                      className="w-full outline-none border-none focus:ring-0 p-0 text-black"
                    />
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
                <div className="flex gap-2">
                  <button
                    onClick={handleSaveEdit}
                    className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => {
                      setEditing(false);
                      setFullName(candidate.full_name);
                      setPhone(candidate.phone || '');
                      setSkills(candidate.skills || []);
                      setProfileLinks(candidate.profile_links || {});
                    }}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 flex-wrap">
            <label className="cursor-pointer px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm">
              📤 Upload Resume
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleResumeUpload(file);
                }}
              />
            </label>
            <label className="cursor-pointer px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm">
              ✨ Enrich Profile
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleEnrichProfile(file);
                }}
              />
            </label>
          </div>

          {/* Applications Section */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                Applications ({applications.length})
              </h3>
              <button
                onClick={() => setShowApplicationForm(!showApplicationForm)}
                className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                {showApplicationForm ? 'Cancel' : '+ Apply to Job'}
              </button>
            </div>

            {showApplicationForm && (
              <form onSubmit={handleApplyToJob} className="mb-4 p-4 bg-gray-50 rounded-lg">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Title
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    required
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g., Senior Developer"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-black"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  >
                    Apply
                  </button>
                </div>
              </form>
            )}

            <div className="space-y-3">
              {applications.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  No applications yet. Click "Apply to Job" to get started!
                </p>
              ) : (
                applications.map((app) => (
                  <div
                    key={app.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{app.job_title}</p>
                    </div>
                    <select
                      value={app.status}
                      onChange={(e) =>
                        handleStatusChange(app.id, e.target.value as ApplicationStatus)
                      }
                      className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(
                        app.status
                      )}`}
                    >
                      {Object.values(ApplicationStatus).map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
