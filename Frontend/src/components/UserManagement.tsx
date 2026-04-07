import { useState, useMemo, useEffect } from 'react';
import { StaffTable } from './StaffTable';
import { AddUserModal } from './modal/AddUserModal';
import EditUserModal from './modal/EditUserModal';
import DeleteUserModal from './modal/DeleteUserModal';
// Remove invalid top-level hook calls. All hooks must be inside the component.
import { Card } from "./ui/card";
import { KPICard } from "./KPICard";
import { User, Users, UserCheck, UserX, Search, Plus, RotateCcw, Loader } from "lucide-react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import apiClient from '../services/api';
import { convertApiUserToUi } from '../utils/conversions';
import { useAuth } from '../context/AuthContext';

interface StaffMember {
  id: number;
  employeeId: string;
  name: string;
  username: string;
  nic: string;
  role: string;
  roleColor: string;
  status: 'Active' | 'Inactive';
  contact: string;
  lastLogin: string;
  avatarColor?: string;
  isActive: boolean; // New field for soft delete filtering
}

const initialStaffMembers: StaffMember[] = [
  {
    id: 1,
    employeeId: '#EMP001',
    name: 'Kamal Perera',
    username: 'kamal.perera',
    nic: '901234567V',
    role: 'Baker',
    roleColor: 'blue',
    status: 'Active',
    contact: '077-1234567',
    lastLogin: 'Yesterday, 4 PM',
    avatarColor: 'bg-blue-200',
    isActive: true,
  },
  {
    id: 2,
    employeeId: '#EMP002',
    name: 'Nimali Silva',
    username: 'nimali.silva',
    nic: '921234568V',
    role: 'Cashier',
    roleColor: 'green',
    status: 'Active',
    contact: '071-9876543',
    lastLogin: 'Today, 9 AM',
    avatarColor: 'bg-green-200',
    isActive: true,
  },
  {
    id: 3,
    employeeId: '#EMP003',
    name: 'Saman Kumara',
    username: 'saman.kumara',
    nic: '881234569V',
    role: 'Storekeeper',
    roleColor: 'orange',
    status: 'Inactive',
    contact: '075-5555555',
    lastLogin: '2 days ago',
    avatarColor: 'bg-orange-200',
    isActive: true,
  },
  {
    id: 4,
    employeeId: '#EMP004',
    name: 'Anura Fernando',
    username: 'anura.fernando',
    nic: '851234570V',
    role: 'Manager',
    roleColor: 'purple',
    status: 'Active',
    contact: '076-1111111',
    lastLogin: 'Today, 10 AM',
    avatarColor: 'bg-purple-200',
    isActive: true,
  },
];


export function UserManagement() {
  const { user } = useAuth();

  if (user?.role !== 'Manager') {
    return (
      <div className="p-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 font-semibold">
          Access Denied: You do not have permission to view User Management.
        </div>
      </div>
    );
  }

  // --- State: API Data ---
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  
  const [editUserOpen, setEditUserOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<StaffMember | null>(null);
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [addUserOpen, setAddUserOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [deleteUserOpen, setDeleteUserOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<StaffMember | null>(null);

  // --- Fetch Users from API ---
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setIsLoading(true);
        setFetchError(null);
        const response = await apiClient.users.getAll();
        // response.items already contains UI-formatted users
        const uiUsers = response.items.map((uiUser: any) => ({
          id: uiUser.id,
          employeeId: uiUser.employee_id,
          name: uiUser.name,
          username: uiUser.username || '',
          nic: uiUser.nic,
          role: uiUser.role,
          roleColor: getRoleColor(uiUser.role),
          status: (uiUser.status === 'active' ? 'Active' : 'Inactive') as 'Active' | 'Inactive',
          contact: uiUser.contact,
          lastLogin: 'N/A', // Backend doesn't track this
          avatarColor: uiUser.avatarColor,
          isActive: uiUser.is_active ?? true, // Default to true if not provided
        }));
        setStaff(uiUsers);
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Failed to fetch users';
        setFetchError(errorMsg);
        console.error('Error fetching users:', error);
        // Fall back to initial mock data
        setStaff(initialStaffMembers.map(user => ({ ...user, isActive: true })));
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, []);

  // Helper to get role color
  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      'Baker': 'blue',
      'Cashier': 'green',
      'Storekeeper': 'orange',
      'Manager': 'purple',
    };
    return colors[role] || 'gray';
  };

  const filteredStaff = useMemo(() => {
    return staff
      // Filter 1: Exclude soft-deleted users (where isActive === false)
      .filter(member => member.isActive === true)
      // Filter 2: Apply search and role/status filters
      .filter(member => {
        const matchesSearch = searchTerm === '' || 
          member.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
          member.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
          member.nic.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesRole = roleFilter === 'all' || member.role.toLowerCase() === roleFilter.toLowerCase();
        const matchesStatus = statusFilter === 'all' || member.status.toLowerCase() === statusFilter.toLowerCase();
        return matchesSearch && matchesRole && matchesStatus;
      });
  }, [staff, searchTerm, roleFilter, statusFilter]);

  const totalUsers = filteredStaff.length;
  const activeUsers = filteredStaff.filter(m => m.status === 'Active').length;
  const inactiveUsers = filteredStaff.filter(m => m.status === 'Inactive').length;

  const resetFilters = () => {
    setSearchTerm('');
    setRoleFilter('all');
    setStatusFilter('all');
  };

  // Refetch users from API (called after user creation/update/delete via onSuccess)
  const refetchUsers = async () => {
    try {
      const response = await apiClient.users.getAll();
      const uiUsers = response.items.map((uiUser: any) => ({
        id: uiUser.id,
        employeeId: uiUser.employee_id,
        name: uiUser.name,
        username: uiUser.username || '',
        nic: uiUser.nic,
        role: uiUser.role,
        roleColor: getRoleColor(uiUser.role),
        status: (uiUser.status === 'active' ? 'Active' : 'Inactive') as 'Active' | 'Inactive',
        contact: uiUser.contact,
        lastLogin: 'N/A',
        avatarColor: uiUser.avatarColor,
        isActive: uiUser.is_active ?? true, // Default to true if not provided
      }));
      setStaff(uiUsers);
    } catch (error) {
      console.error('Error refetching users:', error);
    }
  };

  return (
    <div className="p-8">
      <AddUserModal
        open={addUserOpen}
        onClose={() => setAddUserOpen(false)}
        onSuccess={refetchUsers}
      />
      {/* Add New User Button */}
      <div className="flex justify-end mb-4">
        <button
          className="px-4 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 flex items-center gap-2 transition-colors"
          onClick={() => setAddUserOpen(true)}
        >
          <Plus className="w-5 h-5" />
          Add New User
        </button>
      </div>
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-orange-50 border border-orange-200">
          <div className="p-3 rounded bg-white text-orange-600">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-orange-800 font-semibold">Total Users</div>
            <div className="text-lg font-bold text-orange-700">{totalUsers}</div>
          </div>
        </div>
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-green-50 border border-green-200">
          <div className="p-3 rounded bg-white text-green-600">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-green-800 font-semibold">Active Users</div>
            <div className="text-lg font-bold text-green-700">{activeUsers}</div>
          </div>
        </div>
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
          <div className="p-3 rounded bg-white text-red-600">
            <UserX className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-red-800 font-semibold">Inactive Users</div>
            <div className="text-lg font-bold text-red-700">{inactiveUsers}</div>
          </div>
        </div>
      </div>

      {/* Filters Toolbar */}
      <div className="bg-white p-4 rounded-lg shadow-sm mb-6 flex flex-wrap gap-4 items-center">
        <div className="flex flex-row w-full items-center gap-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-orange-300 w-4 h-4" />
            <Input 
              placeholder="Search by name, username..." 
              className="pl-10 px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 w-64 focus:outline-none focus:ring-2 focus:ring-orange-400 placeholder-orange-300" 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          {/* Role Dropdown */}
          <select 
            value={roleFilter} 
            onChange={(e) => setRoleFilter(e.target.value)} 
            className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 focus:outline-none focus:ring-2 focus:ring-orange-400 cursor-pointer"
          >
            <option value="all">All Roles</option>
            <option value="Manager">Manager</option>
            <option value="Cashier">Cashier</option>
            <option value="Baker">Baker</option>
            <option value="Storekeeper">Storekeeper</option>
          </select>
          {/* Status Dropdown */}
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)} 
            className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 focus:outline-none focus:ring-2 focus:ring-orange-400 cursor-pointer"
          >
            <option value="all">All Status</option>
            <option value="Active">Active</option>
            <option value="Inactive">Inactive</option>
          </select>
          {/* Reset Button */}
          <Button 
            variant="ghost" 
            className="ml-2 flex items-center gap-2 text-orange-600 hover:text-orange-700 hover:bg-orange-50 px-3 py-2 rounded-lg border border-transparent hover:border-orange-200 transition-all duration-200 shadow-sm" 
            onClick={resetFilters}
          >
            <RotateCcw className="w-4 h-4" /> 
            Reset Filters
          </Button>
        </div>
      </div>

      {/* Enhanced Staff Table */}

      <StaffTable 
        staffMembers={filteredStaff} 
        onEdit={user => {
          setSelectedUser(user);
          setEditUserOpen(true);
        }}
        onDelete={user => {
          setUserToDelete(user);
          setDeleteUserOpen(true);
        }}
      />
      <DeleteUserModal
        open={deleteUserOpen}
        onClose={() => setDeleteUserOpen(false)}
        userId={userToDelete?.id}
        onConfirm={async (deletedUserId) => {
          // Remove the user from local state after successful API deletion
          setStaff(prev => prev.filter(u => u.id !== deletedUserId));
        }}
        userName={userToDelete ? userToDelete.name : ''}
      />

      <EditUserModal
        open={editUserOpen}
        onClose={() => setEditUserOpen(false)}
        user={selectedUser ? {
          id: selectedUser.id,
          fullName: selectedUser.name,
          nic: selectedUser.nic,
          contact: selectedUser.contact,
          username: selectedUser.username,
          role: selectedUser.role as any,
          status: selectedUser.status,
        } : null}
        onSuccess={refetchUsers}
        onUpdate={updatedUser => {
          setStaff(prev => prev.map(u =>
            u.id === updatedUser.id
              ? {
                  ...u,
                  name: updatedUser.fullName,
                  username: updatedUser.username,
                  nic: updatedUser.nic,
                  contact: updatedUser.contact,
                  role: updatedUser.role,
                  status: updatedUser.status,
                }
              : u
          ));
        }}
      />
    </div>
  );
}
