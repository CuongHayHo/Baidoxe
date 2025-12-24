import React, { useEffect, useState } from 'react';
import useElectron from '../useElectron';
import './AboutDialog.css';

interface AppInfo {
  version: string;
  name: string;
  releaseDate?: string;
  updateAvailable?: boolean;
}

interface AboutDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AboutDialog({ isOpen, onClose }: AboutDialogProps) {
  const { isElectron, getAppVersion, checkUpdates } = useElectron();
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isOpen) return;

    const loadAppInfo = async () => {
      setLoading(true);
      try {
        const version = await getAppVersion?.();
        const result = await checkUpdates?.();
        const updateAvailable = (result ?? false) as boolean;

        setAppInfo({
          version: (version as any)?.version || '1.0.0',
          name: (version as any)?.name || 'Baidoxe',
          updateAvailable: updateAvailable,
        });
      } catch (error) {
        console.error('Failed to load app info:', error);
        setAppInfo({
          version: '1.0.0',
          name: 'Baidoxe',
        });
      } finally {
        setLoading(false);
      }
    };

    loadAppInfo();
  }, [isOpen, getAppVersion, checkUpdates]);

  if (!isOpen) return null;

  return (
    <div className="about-dialog-overlay" onClick={onClose}>
      <div className="about-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="about-header">
          <h2>{appInfo?.name}</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="about-content">
          {loading ? (
            <p className="loading">Loading...</p>
          ) : (
            <>
              <div className="info-row">
                <span className="label">Version:</span>
                <span className="value">{appInfo?.version}</span>
              </div>

              {appInfo?.updateAvailable && (
                <div className="update-available-badge">
                  <span className="badge-icon">⚡</span>
                  <span className="badge-text">Update Available</span>
                </div>
              )}

              <div className="about-description">
                <p>
                  Baidoxe is a modern parking management system with desktop, web, and
                  hardware integration.
                </p>
              </div>

              <div className="about-links">
                <a href="#" onClick={() => window.open('https://github.com', '_blank')}>
                  GitHub Repository
                </a>
                <a href="#" onClick={() => window.open('https://example.com', '_blank')}>
                  Project Website
                </a>
              </div>

              <div className="about-footer">
                <p>© 2025 Baidoxe Team. All rights reserved.</p>
                <p className="license">Licensed under MIT License</p>
              </div>
            </>
          )}
        </div>

        <div className="about-actions">
          {appInfo?.updateAvailable && isElectron && (
            <button className="btn-update" onClick={onClose}>
              Download Update
            </button>
          )}
          <button className="btn-close" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
