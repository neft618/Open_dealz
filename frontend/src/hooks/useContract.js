import { useState, useEffect } from 'react';
import api from '../api/client';

export const useContract = (contractId) => {
  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!contractId) return;

    const fetchContract = async () => {
      try {
        const response = await api.get(`/contracts/${contractId}`);
        setContract(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchContract();
  }, [contractId]);

  return { contract, loading, error, refetch: () => fetchContract() };
};