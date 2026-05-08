import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api/client';
import Avatar from '../../components/ui/Avatar';

const PublicProfilePage = () => {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    fetchProfile();
  }, [id]);

  const fetchProfile = async () => {
    try {
      const response = await api.get(`/users/${id}`);
      setProfile(response.data);
    } catch (error) {
      console.error('Failed to fetch profile');
    }
  };

  if (!profile) return <div>Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Profile</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <Avatar src={profile.avatar} alt={profile.user_id} size="lg" />
          <h2 className="text-xl font-semibold mt-4">{profile.user_id}</h2>
          <p className="text-gray-600">Bio: {profile.bio}</p>
          <p className="text-sm text-gray-500">Skills: {profile.skills}</p>
          <p className="text-sm text-gray-500">Specialization: {profile.specialization}</p>
          <p className="text-sm text-gray-500">Rating: {profile.rating}/5</p>
          <p className="text-sm text-gray-500">Contracts: {profile.contracts_count}</p>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-4">Portfolio</h3>
          <div className="grid grid-cols-2 gap-4">
            {profile.portfolio.map((item) => (
              <div key={item.id} className="border rounded p-2">
                <img src={item.file_url} alt={item.title} className="w-full h-24 object-cover rounded" />
                <p className="text-sm mt-1">{item.title}</p>
                <p className="text-sm text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicProfilePage;