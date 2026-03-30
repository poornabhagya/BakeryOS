import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X, Eye, EyeOff, AlertCircle } from 'lucide-react';
import apiClient from '../../services/api';

interface User {
  id: string | number;
  fullName: string;
  nic: string;
  contact: string;
  username: string;
  role: 'Manager' | 'Cashier' | 'Baker' | 'Storekeeper';
  status: 'Active' | 'Inactive';
}

interface EditUserModalProps {
  open: boolean;
  onClose: () => void;
  user: User | null;
  onUpdate: (updatedUser: any) => void;
  onSuccess?: () => void;
}

const ROLES = ['Manager', 'Cashier', 'Baker', 'Storekeeper'];

const EditUserModal: React.FC<EditUserModalProps> = ({ open, onClose, user, onUpdate, onSuccess }) => {
  const [fullName, setFullName] = useState('');
  const [nic, setNic] = useState('');
  const [contact, setContact] = useState('');
  const [username, setUsername] = useState('');
  const [role, setRole] = useState<User['role']>('Manager');
  const [status, setStatus] = useState<User['status']>('Active');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [touched, setTouched] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    if (open && user) {
      setFullName(user.fullName || '');
      setNic(user.nic || '');
      setContact(user.contact || '');
      setUsername(user.username || '');
      setRole(user.role);
      setStatus(user.status);
      setPassword('');
      setConfirmPassword('');
      setTouched(false);
    }
  }, [open, user]);

  const nameInvalid = !fullName.trim();
  const contactInvalid = !contact.trim();
  const usernameInvalid = !username.trim();
  const roleInvalid = !role;
  const passwordInvalid = password && password.length < 4;
  const confirmInvalid = password ? confirmPassword !== password : false;
  const canSave = !nameInvalid && !contactInvalid && !usernameInvalid && !roleInvalid && (!password || (!passwordInvalid && !confirmInvalid));

  if (!open || !user) return null;

  const handleSave = async () => {
    setTouched(true);
    setApiError(null);
    
    if (!canSave) {
      console.log('[EditUserModal] Form validation failed');
      return;
    }

    setIsSubmitting(true);

    try {
      // Build payload with only updated fields
      const payload: any = {
        full_name: fullName.trim(),
        nic: nic.trim() || '',
        contact: contact.trim() || '',
        role: role,
        status: status === 'Active' ? 'active' : 'inactive',  // Convert frontend status to backend format
      };

      // Only include password if user provided a new one
      if (password.trim()) {
        payload.password = password;
      }

      console.log('[EditUserModal] Submitting update payload:', payload);

      // Make PATCH request to backend
      await apiClient.users.update(Number(user.id), payload);

      console.log('[EditUserModal] User updated successfully');

      // Update parent component state
      onUpdate({
        id: user.id,
        fullName: fullName.trim(),
        nic: nic.trim(),
        contact: contact.trim(),
        username: username.trim(),
        role,
        status,
      });

      // Trigger refresh of user list from API
      if (onSuccess) {
        onSuccess();
      }

      onClose();
    } catch (error) {
      console.error('[EditUserModal] Error updating user:', error);
      const errorMsg = error instanceof Error ? error.message : 'Failed to update user. Please try again.';
      setApiError(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const modalContent = (
    <div className="fixed inset-0 z-[110] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" aria-modal="true" role="dialog">
      <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-orange-100 bg-orange-50/60">
          <h3 className="text-lg font-bold text-orange-800">Edit User - {user.fullName}</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-100 transition-colors" aria-label="Close">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>
        {/* Error Message */}
        {apiError && (
          <div className="mx-6 mt-4 p-3 rounded-lg border border-red-300 bg-red-50 flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{apiError}</p>
          </div>
        )}
        {/* Body */}
        <div className="flex-1 p-6 flex flex-col gap-6">
          {/* Employee ID */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Employee ID</label>
            <input
              type="text"
              value={user.id}
              readOnly
              disabled
              className="w-full bg-gray-100 text-gray-500 rounded-lg px-3 py-2 border border-gray-200 cursor-not-allowed"
            />
          </div>
          {/* Personal Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-orange-50/40 p-4 rounded-lg border border-orange-100">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">Full Name <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                placeholder="e.g. John Doe"
                required
              />
              {touched && nameInvalid && <p className="text-xs text-red-500 mt-1">Full name is required.</p>}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">NIC Number</label>
              <input
                type="text"
                value={nic}
                onChange={e => setNic(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                placeholder="e.g. 123456789V"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">Contact Number <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={contact}
                onChange={e => setContact(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                placeholder="e.g. 077-1234567"
                required
              />
              {touched && contactInvalid && <p className="text-xs text-red-500 mt-1">Contact number is required.</p>}
            </div>
          </div>
          {/* System Access */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-orange-50/40 p-4 rounded-lg border border-orange-100">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">Username <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                placeholder="e.g. johndoe"
                required
              />
              {touched && usernameInvalid && <p className="text-xs text-red-500 mt-1">Username is required.</p>}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">Role <span className="text-red-500">*</span></label>
              <select
                value={role}
                onChange={e => setRole(e.target.value as User['role'])}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                required
              >
                <option value="">Select Role</option>
                {ROLES.map(r => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
              {touched && roleInvalid && <p className="text-xs text-red-500 mt-1">Role is required.</p>}
            </div>
            {/* Password Section */}
            <div className="relative col-span-2">
              <label className="block text-sm font-medium mb-1 text-gray-700">New Password</label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              />
              <button type="button" className="absolute right-2 top-8 transform -translate-y-1/2 text-gray-400 hover:text-orange-500" onClick={() => setShowPassword(v => !v)} tabIndex={-1}>
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
              <p className="text-xs text-gray-400 mt-1">Leave blank to keep current password.</p>
              {touched && passwordInvalid && password && <p className="text-xs text-red-500 mt-1">Password must be at least 4 characters.</p>}
            </div>
            <div className="relative col-span-2">
              <label className="block text-sm font-medium mb-1 text-gray-700">Confirm New Password</label>
              <input
                type={showConfirm ? 'text' : 'password'}
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              />
              <button type="button" className="absolute right-2 top-8 transform -translate-y-1/2 text-gray-400 hover:text-orange-500" onClick={() => setShowConfirm(v => !v)} tabIndex={-1}>
                {showConfirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
              {touched && confirmInvalid && password && <p className="text-xs text-red-500 mt-1">Passwords must match.</p>}
            </div>
          </div>
          {/* Status */}
          <div className="flex items-center gap-4">
            <label className="block text-sm font-medium text-gray-700">Status</label>
            <select
              value={status}
              onChange={e => setStatus(e.target.value as User['status'])}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
            >
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
            </select>
          </div>
        </div>
        {/* Footer */}
        <div className="p-4 bg-gray-50 border-t border-orange-100 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 font-medium transition-colors disabled:opacity-60"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={!canSave || isSubmitting}
            className="px-4 py-2 rounded-lg bg-orange-600 text-white font-bold hover:bg-orange-700 transition-colors disabled:opacity-60 flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Saving...
              </>
            ) : (
              'Save Changes'
            )}
          </button>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

export default EditUserModal;
