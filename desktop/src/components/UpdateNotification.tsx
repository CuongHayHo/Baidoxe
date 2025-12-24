import React, { useEffect, useState } from 'react';
import useElectron from '../useElectron';
import './UpdateNotification.css';

interface UpdateStatus {
  available: boolean;
  downloaded: boolean;
  checking: boolean;
  version?: string;
  error?: string;
}

export default function UpdateNotification() {
  const {
    isElectron,
    onUpdateAvailable,
    onUpdateDownloaded,
    onUpdateError,
    onCheckingForUpdate,
    installUpdate,
  } = useElectron();

  const [updateStatus, setUpdateStatus] = useState<UpdateStatus>({
    available: false,
    downloaded: false,
    checking: false,
  });

  useEffect(() => {
    if (!isElectron) return;

    // Listen for checking-for-update event
    onCheckingForUpdate?.(() => {
      setUpdateStatus((prev: UpdateStatus) => ({ ...prev, checking: true }));
    });

    // Listen for update-available event
    onUpdateAvailable?.((data: any) => {
      setUpdateStatus({
        available: true,
        downloaded: false,
        checking: false,
        version: data.version,
      });
    });

    // Listen for update-downloaded event
    onUpdateDownloaded?.((data: any) => {
      setUpdateStatus({
        available: true,
        downloaded: true,
        checking: false,
        version: data.version,
      });
    });

    // Listen for update-error event
    onUpdateError?.((data: any) => {
      setUpdateStatus((prev: UpdateStatus) => ({
        ...prev,
        checking: false,
        error: data.message,
      }));
    });
  }, [isElectron, onCheckingForUpdate, onUpdateAvailable, onUpdateDownloaded, onUpdateError]);

  if (!isElectron || !updateStatus.downloaded) return null;

  return (
    <div className="update-notification-container">
      <div className="update-banner">
        <div className="update-content">
          <h3>Update Available</h3>
          <p>Version {updateStatus.version} is ready to install.</p>
        </div>
        <div className="update-actions">
          <button
            onClick={() => {
              installUpdate?.();
            }}
            className="btn-primary"
          >
            Restart & Update
          </button>
          <button
            onClick={() =>
              setUpdateStatus((prev: UpdateStatus) => ({ ...prev, downloaded: false }))
            }
            className="btn-secondary"
          >
            Later
          </button>
        </div>
      </div>
    </div>
  );
}
