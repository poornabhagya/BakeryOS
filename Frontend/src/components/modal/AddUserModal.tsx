import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X, Eye, EyeOff, AlertCircle, Loader, CheckCircle } from 'lucide-react';
import apiClient from '../../services/api';

interface AddUserModalProps {
  open: boolean;
  onClose: () => void;
  onSave?: (userData: any) => void;
  onSuccess?: () => void;
}

interface FieldErrors {
  username?: string[];
  password?: string[];
  password_confirm?: string[];
  full_name?: string[];
  contact?: string[];
  nic?: string[];
  email?: string[];
  role?: string[];
  [key: string]: string[] | undefined;
}

const ROLES = ['Manager', 'Cashier', 'Baker', 'Storekeeper'];

const genEmployeeId = (lastId: number) => `EMP-${String(lastId + 1).padStart(3, '0')}`;

// Password validation requirements
const PASSWORD_MIN_LENGTH = 8;
const validatePasswordStrength = (pwd: string) => {
  const checks = {
    minLength: pwd.length >= PASSWORD_MIN_LENGTH,
    hasUpperCase: /[A-Z]/.test(pwd),
    hasLowerCase: /[a-z]/.test(pwd),
    hasNumber: /[0-9]/.test(pwd),
  };
  return checks;
};

// Extract field-level validation errors from Django REST Framework response
const extractErrorDetails = (error: any): FieldErrors => {
  const errors: FieldErrors = {};

  // If error has details from API response (from ApiError)
  if (error?.details) {
    // Assume it's already a field errors object from DRF
    Object.keys(error.details).forEach(key => {
      const value = error.details[key];
      // DRF returns errors as arrays of strings
      errors[key] = Array.isArray(value) ? value : [String(value)];
    });
  }

  return errors;
};

export const AddUserModal: React.FC<AddUserModalProps> = ({ open, onClose, onSave, onSuccess }) => {
  const [employeeId, setEmployeeId] = useState('EMP-001');
  const [fullName, setFullName] = useState('');
  const [nic, setNic] = useState('');
  const [contact, setContact] = useState('');
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [status, setStatus] = useState<'active' | 'inactive'>('active');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [touched, setTouched] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});

  useEffect(() => {
    if (open) {
      setEmployeeId(genEmployeeId(4));
      setFullName('');
      setNic('');
      setContact('');
      setUsername('');
      setRole('');
      setPassword('');
      setConfirmPassword('');
      setStatus('active');
      setShowPassword(false);
      setShowConfirm(false);
      setTouched(false);
      setApiError(null);
      setFieldErrors({});
    }
  }, [open]);

  // Frontend validation checks
  const nameInvalid = !fullName.trim();
  const contactInvalid = !contact.trim();
  const usernameInvalid = !username.trim() || username.length < 3;
  const roleInvalid = !role;
  const passwordStrength = validatePasswordStrength(password);
  const passwordInvalid = !password || !passwordStrength.minLength || !passwordStrength.hasUpperCase || !passwordStrength.hasLowerCase || !passwordStrength.hasNumber;
  
  // Confirm password validation with granular error messages
  const confirmPasswordEmpty = !confirmPassword;
  const confirmPasswordMismatch = confirmPassword && confirmPassword !== password;
  const confirmInvalid = confirmPasswordEmpty || confirmPasswordMismatch;
  
  const canSave = !nameInvalid && !contactInvalid && !usernameInvalid && !roleInvalid && !passwordInvalid && !confirmInvalid;

  if (!open) return null;

  const handleSave = async () => {
    setTouched(true);
    setApiError(null);
    setFieldErrors({});
    
    if (!canSave) {
      console.log('[AddUserModal] Form validation failed');
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = {
        username: username.trim(),
        password: password,
        password_confirm: confirmPassword,
        full_name: fullName.trim(),
        role: role,
        nic: nic.trim() || '',
        contact: contact.trim() || '',
      };

      console.log('[AddUserModal] Submitting user payload:', payload);
      const response = await apiClient.users.create(payload);

      console.log('[AddUserModal] User created successfully:', response);

      if (onSave) {
        const userData = {
          username: username.trim(),
          fullName: fullName.trim(),
          nic: nic.trim(),
          contact: contact.trim(),
          role,
        };
        onSave(userData);
      }

      if (onSuccess) {
        onSuccess();
      }

      onClose();
    } catch (error) {
      console.error('[AddUserModal] Error creating user:', error);
      
      // Extract field-level errors from backend
      const extractedErrors = extractErrorDetails(error);
      
      if (Object.keys(extractedErrors).length > 0) {
        // Display field-specific errors
        setFieldErrors(extractedErrors);
        setApiError('Please fix the errors below and try again.');
      } else {
        // Generic error message
        const errorMsg = error instanceof Error ? error.message : 'Failed to create user. Please try again.';
        setApiError(errorMsg);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get error message for a specific field
  const getFieldError = (fieldName: keyof FieldErrors): string | null => {
    const errors = fieldErrors[fieldName];
    if (errors && errors.length > 0) {
      return errors.join('; ');
    }
    return null;
  };

  const modalContent = (
    <div className="fixed inset-0 z-[110] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" aria-modal="true" role="dialog">
      <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100 animate-fade-in max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-orange-100 bg-orange-50/60 sticky top-0">
          <h3 className="text-lg font-bold text-orange-800">Add New User</h3>
          <button 
            onClick={onClose} 
            disabled={isSubmitting}
            className="p-2 rounded-lg hover:bg-orange-100 transition-colors disabled:opacity-50" 
            aria-label="Close"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>
        
        {/* Body */}
        <div className="flex-1 p-6 flex flex-col gap-6">
          {/* Validation Errors Alert */}
          {(apiError || Object.keys(fieldErrors).length > 0) && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start gap-3 mb-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-800">Validation Error</p>
                  {apiError && <p className="text-sm text-red-700 mt-1">{apiError}</p>}
                </div>
              </div>
              
              {/* Detailed Field Errors */}
              {Object.keys(fieldErrors).length > 0 && (
                <div className="ml-8 space-y-2">
                  {Object.entries(fieldErrors).map(([field, errors]) => (
                    <div key={field} className="text-sm text-red-700">
                      <span className="font-medium capitalize">{field.replace(/_/g, ' ')}:</span>
                      <ul className="list-disc list-inside ml-2">
                        {errors?.map((err, idx) => (
                          <li key={idx}>{err}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Employee ID */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Employee ID</label>
            <input
              type="text"
              value={employeeId}
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
                disabled={isSubmitting}
                className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:border-transparent transition-all disabled:opacity-50 ${
                  getFieldError('full_name') ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-orange-500'
                }`}
                placeholder="e.g. John Doe"
              />
              {getFieldError('full_name') && (
                <p className="text-xs text-red-500 mt-1">{getFieldError('full_name')}</p>
              )}
              {touched && nameInvalid && !getFieldError('full_name') && (
                <p className="text-xs text-red-500 mt-1">Full name is required.</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">NIC Number</label>
              <input
                type="text"
                value={nic}
                onChange={e => setNic(e.target.value)}
                disabled={isSubmitting}
                className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:border-transparent transition-all disabled:opacity-50 ${
                  getFieldError('nic') ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-orange-500'
                }`}
                placeholder="e.g. 123456789V"
              />
              {getFieldError('nic') && (
                <p className="text-xs text-red-500 mt-1">{getFieldError('nic')}</p>
              )}
              <p className="text-xs text-gray-500 mt-1">Format: 9 digits + V/X or 12 digits</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">Contact Number <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={contact}
                onChange={e => setContact(e.target.value)}
                disabled={isSubmitting}
                className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:border-transparent transition-all disabled:opacity-50 ${
                  getFieldError('contact') ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-orange-500'
                }`}
                placeholder="e.g. 077-1234567"
              />
              {getFieldError('contact') && (
                <p className="text-xs text-red-500 mt-1">{getFieldError('contact')}</p>
              )}
              {touched && contactInvalid && !getFieldError('contact') && (
                <p className="text-xs text-red-500 mt-1">Contact number is required.</p>
              )}
            </div>
          </div>

          {/* System Access */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-orange-50/40 p-4 rounded-lg border border-orange-100">
            {/* Username */}
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">Username <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                disabled={isSubmitting}
                className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:border-transparent transition-all disabled:opacity-50 ${
                  getFieldError('username') ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-orange-500'
                }`}
                placeholder="e.g. johndoe"
                minLength={3}
              />
              {getFieldError('username') && (
                <p className="text-xs text-red-500 mt-1">{getFieldError('username')}</p>
              )}
              {touched && usernameInvalid && !getFieldError('username') && (
                <p className="text-xs text-red-500 mt-1">Username must be at least 3 characters.</p>
              )}
              <p className="text-xs text-gray-500 mt-1">3+ characters, alphanumeric + underscore</p>
            </div>

            {/* Role */}
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">Role <span className="text-red-500">*</span></label>
              <select
                value={role}
                onChange={e => setRole(e.target.value)}
                disabled={isSubmitting}
                className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:border-transparent transition-all disabled:opacity-50 ${
                  getFieldError('role') ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-orange-500'
                }`}
              >
                <option value="">Select Role</option>
                {ROLES.map(r => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
              {getFieldError('role') && (
                <p className="text-xs text-red-500 mt-1">{getFieldError('role')}</p>
              )}
              {touched && roleInvalid && !getFieldError('role') && (
                <p className="text-xs text-red-500 mt-1">Role is required.</p>
              )}
            </div>

            {/* Password */}
            <div className="relative">
              <label className="block text-sm font-medium mb-1 text-gray-700">Password <span className="text-red-500">*</span></label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                disabled={isSubmitting}
                className={`w-full border rounded-lg px-3 py-2 pr-10 focus:outline-none focus:ring-2 focus:border-transparent transition-all disabled:opacity-50 ${
                  getFieldError('password') ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-orange-500'
                }`}
              />
              <button 
                type="button" 
                className="absolute right-2 top-10 transform -translate-y-1/2 text-gray-400 hover:text-orange-500 disabled:opacity-50" 
                onClick={() => setShowPassword(v => !v)} 
                tabIndex={-1}
                disabled={isSubmitting}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
              
              {getFieldError('password') && (
                <p className="text-xs text-red-500 mt-1">{getFieldError('password')}</p>
              )}
              
              {/* Password strength indicator */}
              {password && (
                <div className="mt-2 space-y-1">
                  <p className="text-xs font-medium text-gray-600">Password Requirements:</p>
                  <div className="space-y-0.5 text-xs">
                    <div className="flex items-center gap-1.5">
                      {passwordStrength.minLength ? (
                        <CheckCircle className="w-3.5 h-3.5 text-green-500" />
                      ) : (
                        <AlertCircle className="w-3.5 h-3.5 text-gray-300" />
                      )}
                      <span className={passwordStrength.minLength ? 'text-green-700' : 'text-gray-500'}>
                        At least {PASSWORD_MIN_LENGTH} characters
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {passwordStrength.hasUpperCase ? (
                        <CheckCircle className="w-3.5 h-3.5 text-green-500" />
                      ) : (
                        <AlertCircle className="w-3.5 h-3.5 text-gray-300" />
                      )}
                      <span className={passwordStrength.hasUpperCase ? 'text-green-700' : 'text-gray-500'}>
                        One uppercase letter
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {passwordStrength.hasLowerCase ? (
                        <CheckCircle className="w-3.5 h-3.5 text-green-500" />
                      ) : (
                        <AlertCircle className="w-3.5 h-3.5 text-gray-300" />
                      )}
                      <span className={passwordStrength.hasLowerCase ? 'text-green-700' : 'text-gray-500'}>
                        One lowercase letter
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {passwordStrength.hasNumber ? (
                        <CheckCircle className="w-3.5 h-3.5 text-green-500" />
                      ) : (
                        <AlertCircle className="w-3.5 h-3.5 text-gray-300" />
                      )}
                      <span className={passwordStrength.hasNumber ? 'text-green-700' : 'text-gray-500'}>
                        One number
                      </span>
                    </div>
                  </div>
                </div>
              )}
              
              {touched && passwordInvalid && !password && !getFieldError('password') && (
                <p className="text-xs text-red-500 mt-1">Password is required.</p>
              )}
            </div>

            {/* Confirm Password */}
            <div className="relative">
              <label className="block text-sm font-medium mb-1 text-gray-700">Confirm Password <span className="text-red-500">*</span></label>
              <input
                type={showConfirm ? 'text' : 'password'}
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                disabled={isSubmitting}
                className={`w-full border rounded-lg px-3 py-2 pr-10 focus:outline-none focus:ring-2 focus:border-transparent transition-all disabled:opacity-50 ${
                  getFieldError('password_confirm') || (touched && confirmInvalid)
                    ? 'border-red-300 focus:ring-red-500'
                    : 'border-gray-300 focus:ring-orange-500'
                }`}
              />
              <button 
                type="button" 
                className="absolute right-2 top-10 transform -translate-y-1/2 text-gray-400 hover:text-orange-500 disabled:opacity-50" 
                onClick={() => setShowConfirm(v => !v)} 
                tabIndex={-1}
                disabled={isSubmitting}
              >
                {showConfirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
              
              {getFieldError('password_confirm') && (
                <p className="text-xs text-red-500 mt-1">{getFieldError('password_confirm')}</p>
              )}
              {touched && !getFieldError('password_confirm') && (
                <>
                  {confirmPasswordEmpty && (
                    <p className="text-xs text-red-500 mt-1">This field is required.</p>
                  )}
                  {confirmPasswordMismatch && (
                    <p className="text-xs text-red-500 mt-1">Passwords do not match.</p>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Status */}
          <div className="flex items-center gap-4">
            <label className="block text-sm font-medium text-gray-700">Status</label>
            <select
              value={status}
              onChange={e => setStatus(e.target.value as 'active' | 'inactive')}
              disabled={isSubmitting}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all disabled:opacity-50"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-gray-50 border-t border-orange-100 flex items-center justify-end gap-2 sticky bottom-0">
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={!canSave || isSubmitting}
            className="px-4 py-2 rounded-lg bg-orange-600 text-white font-bold hover:bg-orange-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Creating...
              </>
            ) : (
              'Save User'
            )}
          </button>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
