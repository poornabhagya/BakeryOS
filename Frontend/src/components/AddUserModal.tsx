import { X, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import apiClient from '../services/api';

interface AddUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function AddUserModal({ isOpen, onClose, onSuccess }: AddUserModalProps) {
  const [formData, setFormData] = useState({
    employeeId: '',
    fullName: '',
    nicNumber: '',
    contactNumber: '',
    username: '',
    password: '',
    confirmPassword: '',
    role: 'Cashier',
    status: 'active',
  });

  const [errors, setErrors] = useState<Partial<typeof formData>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  if (!isOpen) return null;

  // Validation function
  const validateForm = (): boolean => {
    const newErrors: Partial<typeof formData> = {};

    // Required fields validation
    if (!formData.employeeId.trim()) newErrors.employeeId = 'Employee ID is required';
    if (!formData.fullName.trim()) newErrors.fullName = 'Full Name is required';
    if (!formData.username.trim()) newErrors.username = 'Username is required';
    if (!formData.password) newErrors.password = 'Password is required';
    if (!formData.confirmPassword) newErrors.confirmPassword = 'Confirm Password is required';

    // Password validation
    if (formData.password && formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Password confirmation validation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Username validation
    if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);

    // Validate form
    if (!validateForm()) {
      console.log('[AddUserModal] Form validation failed');
      return;
    }

    setIsSubmitting(true);

    try {
      // Construct the payload to match Django custom User model
      const payload = {
        employee_id: formData.employeeId.trim(),
        full_name: formData.fullName.trim(),
        nic: formData.nicNumber.trim() || null,
        contact: formData.contactNumber.trim() || null,
        username: formData.username.trim(),
        password: formData.password,
        role: formData.role,
        status: formData.status,
      };

      console.log('[AddUserModal] Submitting user payload:', payload);

      // Make API call to create user
      await apiClient.users.create(payload);

      console.log('[AddUserModal] User created successfully');

      // Reset form
      setFormData({
        employeeId: '',
        fullName: '',
        nicNumber: '',
        contactNumber: '',
        username: '',
        password: '',
        confirmPassword: '',
        role: 'Cashier',
        status: 'active',
      });

      // Notify parent component of success
      if (onSuccess) {
        onSuccess();
      }

      // Close modal
      onClose();
    } catch (error) {
      const errorMsg =
        error instanceof Error ? error.message : 'Failed to create user. Please try again.';
      console.error('[AddUserModal] Error creating user:', error);
      setApiError(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setErrors({});
    setApiError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 sticky top-0 bg-white">
          <h3 className="text-xl font-semibold text-gray-900">Add New User</h3>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* API Error Alert */}
          {apiError && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{apiError}</p>
            </div>
          )}

          {/* Employee ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Employee ID *
            </label>
            <input
              type="text"
              value={formData.employeeId}
              onChange={(e) => {
                setFormData({ ...formData, employeeId: e.target.value });
                if (errors.employeeId) setErrors({ ...errors, employeeId: undefined });
              }}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent ${
                errors.employeeId ? 'border-red-500 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="e.g., EMP-001"
              disabled={isSubmitting}
            />
            {errors.employeeId && (
              <p className="text-sm text-red-600 mt-1">{errors.employeeId}</p>
            )}
          </div>

          {/* Full Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              value={formData.fullName}
              onChange={(e) => {
                setFormData({ ...formData, fullName: e.target.value });
                if (errors.fullName) setErrors({ ...errors, fullName: undefined });
              }}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent ${
                errors.fullName ? 'border-red-500 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="e.g., John Doe"
              disabled={isSubmitting}
            />
            {errors.fullName && (
              <p className="text-sm text-red-600 mt-1">{errors.fullName}</p>
            )}
          </div>

          {/* NIC Number */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              NIC Number
            </label>
            <input
              type="text"
              value={formData.nicNumber}
              onChange={(e) => setFormData({ ...formData, nicNumber: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="e.g., 123456789V"
              disabled={isSubmitting}
            />
          </div>

          {/* Contact Number */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contact Number
            </label>
            <input
              type="tel"
              value={formData.contactNumber}
              onChange={(e) => setFormData({ ...formData, contactNumber: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="e.g., 0771234567"
              disabled={isSubmitting}
            />
          </div>

          {/* Username */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username *
            </label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => {
                setFormData({ ...formData, username: e.target.value });
                if (errors.username) setErrors({ ...errors, username: undefined });
              }}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent ${
                errors.username ? 'border-red-500 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="e.g., johndoe"
              disabled={isSubmitting}
            />
            {errors.username && (
              <p className="text-sm text-red-600 mt-1">{errors.username}</p>
            )}
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password *
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => {
                setFormData({ ...formData, password: e.target.value });
                if (errors.password) setErrors({ ...errors, password: undefined });
              }}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent ${
                errors.password ? 'border-red-500 bg-red-50' : 'border-gray-300'
              }`}
              placeholder="Minimum 8 characters"
              disabled={isSubmitting}
            />
            {errors.password && (
              <p className="text-sm text-red-600 mt-1">{errors.password}</p>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password *
            </label>
            <input
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => {
                setFormData({ ...formData, confirmPassword: e.target.value });
                if (errors.confirmPassword)
                  setErrors({ ...errors, confirmPassword: undefined });
              }}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent ${
                errors.confirmPassword
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-300'
              }`}
              placeholder="Re-enter password"
              disabled={isSubmitting}
            />
            {errors.confirmPassword && (
              <p className="text-sm text-red-600 mt-1">{errors.confirmPassword}</p>
            )}
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Role *
            </label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              disabled={isSubmitting}
            >
              <option value="Baker">Baker</option>
              <option value="Cashier">Cashier</option>
              <option value="Storekeeper">Storekeeper</option>
              <option value="Manager">Manager</option>
            </select>
          </div>

          {/* Status Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status *
            </label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              disabled={isSubmitting}
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
            </select>
          </div>

          {/* Modal Footer */}
          <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
