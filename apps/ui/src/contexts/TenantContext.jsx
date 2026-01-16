import React, { createContext, useContext, useState, useEffect } from 'react';
import { adminAPI } from '../services/api';

const TenantContext = createContext();

export const TenantProvider = ({ children }) => {
  const [currentTenant, setCurrentTenant] = useState(null);
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load tenants on mount
  useEffect(() => {
    loadTenants();
  }, []);

  const loadTenants = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.tenants.getAll();
      setTenants(response.data || response);
      
      // Set first tenant as current if none selected
      if (!currentTenant && response.length > 0) {
        setCurrentTenant(response[0]);
        localStorage.setItem('tenantId', response[0].id);
      }
      setError(null);
    } catch (err) {
      console.error('Error loading tenants:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const switchTenant = (tenantId) => {
    const tenant = tenants.find(t => t.id === tenantId);
    if (tenant) {
      setCurrentTenant(tenant);
      localStorage.setItem('tenantId', tenantId);
    }
  };

  const createTenant = async (tenantData) => {
    try {
      const response = await adminAPI.tenants.create(tenantData);
      const newTenant = response.data || response;
      setTenants([...tenants, newTenant]);
      return newTenant;
    } catch (err) {
      console.error('Error creating tenant:', err);
      throw err;
    }
  };

  const updateTenant = async (tenantId, tenantData) => {
    try {
      const response = await adminAPI.tenants.update(tenantId, tenantData);
      const updatedTenant = response.data || response;
      setTenants(tenants.map(t => t.id === tenantId ? updatedTenant : t));
      if (currentTenant?.id === tenantId) {
        setCurrentTenant(updatedTenant);
      }
      return updatedTenant;
    } catch (err) {
      console.error('Error updating tenant:', err);
      throw err;
    }
  };

  const deleteTenant = async (tenantId) => {
    try {
      await adminAPI.tenants.delete(tenantId);
      setTenants(tenants.filter(t => t.id !== tenantId));
      if (currentTenant?.id === tenantId) {
        setCurrentTenant(tenants[0] || null);
      }
    } catch (err) {
      console.error('Error deleting tenant:', err);
      throw err;
    }
  };

  const value = {
    currentTenant,
    tenants,
    loading,
    error,
    switchTenant,
    createTenant,
    updateTenant,
    deleteTenant,
    reloadTenants: loadTenants,
  };

  return <TenantContext.Provider value={value}>{children}</TenantContext.Provider>;
};

export const useTenant = () => {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
};
