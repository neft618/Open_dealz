import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import FileUpload from '../../components/ui/FileUpload';
import Button from '../../components/ui/Button';
import Avatar from '../../components/ui/Avatar';
import Input from '../../components/ui/Input';
import toast from 'react-hot-toast';

const ProfilePage = () => {
  const [profile, setProfile] = useState({});
  const [portfolio, setPortfolio] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({ bio: '', skills: '', specialization: '' });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/users/me');
      setProfile(response.data);
      setPortfolio(response.data.portfolio || []);
      setFormData({
        bio: response.data.bio || '',
        skills: response.data.skills || '',
        specialization: response.data.specialization || '',
      });
    } catch (error) {
      toast.error('Failed to fetch profile');
    }
  };

  const handleUpdateProfile = async () => {
    try {
      await api.patch('/users/me/profile', formData);
      setEditMode(false);
      fetchProfile();
      toast.success('Profile updated');
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  const handleUploadPortfolio = async (files) => {
    if (files.length === 0) return;
    const formData = new FormData();
    formData.append('file', files[0]);
    formData.append('title', 'Portfolio Item');
    formData.append('description', 'Description');
    try {
      await api.post('/users/me/portfolio', formData);
      fetchProfile();
      toast.success('Portfolio item uploaded');
    } catch (error) {
      toast.error('Failed to upload portfolio');
    }
  };

  const handleDeletePortfolio = async (id) => {
    try {
      await api.delete(`/users/me/portfolio/${id}`);
      fetchProfile();
      toast.success('Portfolio item deleted');
    } catch (error) {
      toast.error('Failed to delete portfolio');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">My Profile</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <Avatar src={profile.avatar} alt={profile.full_name} size="lg" />
          <h2 className="text-xl font-semibold mt-4">{profile.full_name}</h2>
          <p className="text-gray-600">{profile.email}</p>
          <p className="text-sm text-gray-500">Role: {profile.role}</p>
          <p className="text-sm text-gray-500">Rating: {profile.rating}/5</p>
          <p className="text-sm text-gray-500">Contracts: {profile.contracts_count}</p>

          {editMode ? (
            <div className="mt-4">
              <Input label="Bio" value={formData.bio} onChange={(e) => setFormData({ ...formData, bio: e.target.value })} />
              <Input label="Skills" value={formData.skills} onChange={(e) => setFormData({ ...formData, skills: e.target.value })} />
              <select
                value={formData.specialization}
                onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                className="border rounded px-3 py-2 mt-2 w-full"
              >
                <option value="">Select Specialization</option>
                <option value="web_development">Web Development</option>
                <option value="mobile_development">Mobile Development</option>
                <option value="data_science">Data Science</option>
                <option value="design">Design</option>
                <option value="marketing">Marketing</option>
                <option value="other">Other</option>
              </select>
              <div className="mt-4">
                <Button onClick={handleUpdateProfile} className="mr-2">Save</Button>
                <Button onClick={() => setEditMode(false)} variant="secondary">Cancel</Button>
              </div>
            </div>
          ) : (
            <Button onClick={() => setEditMode(true)} className="mt-4">Edit Profile</Button>
          )}
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-4">Portfolio</h3>
          <FileUpload onFileSelect={handleUploadPortfolio} />
          <div className="grid grid-cols-2 gap-4 mt-4">
            {portfolio.map((item) => (
              <div key={item.id} className="border rounded p-2">
                <img src={item.file_url} alt={item.title} className="w-full h-24 object-cover rounded" />
                <p className="text-sm mt-1">{item.title}</p>
                <Button onClick={() => handleDeletePortfolio(item.id)} variant="danger" size="sm" className="mt-1">Delete</Button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;