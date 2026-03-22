
import { useState } from 'react';
import { Edit2, Trash2 } from 'lucide-react';
import { Badge } from './ui/badge';
import { AddUserModal } from './AddUserModal';
import { Avatar, AvatarFallback } from './ui/avatar';

interface StaffMember {
  id: number;
  employeeId: string;
  name: string;
  nic: string;
  role: string;
  roleColor: string;
  status: 'Active' | 'Inactive';
  contact: string;
  lastLogin: string;
  avatarColor?: string;
  
}
  

interface StaffTableProps {
  staffMembers?: StaffMember[];
  onEdit?: (user: StaffMember) => void;
  onDelete?: (user: StaffMember) => void;
}

const defaultStaffMembers: StaffMember[] = [
  {
    id: 1,
    employeeId: '#EMP001',
    name: 'Kamal Perera',
    nic: '851234570V',
    role: 'Baker',
    roleColor: 'blue',
    status: 'Active',
    contact: '077-1234567',
    lastLogin: 'Yesterday, 4 PM',
    avatarColor: 'bg-blue-200',
  },
  {
    id: 2,
    employeeId: '#EMP002',
    name: 'Nimali Silva',
    nic: '851234570V',
    role: 'Cashier',
    roleColor: 'green',
    status: 'Active',
    contact: '071-9876543',
    lastLogin: 'Today, 9 AM',
    avatarColor: 'bg-green-200',
  },
  {
    id: 3,
    employeeId: '#EMP003',
    name: 'Saman Kumara',
    nic: '851234570V',
    role: 'Storekeeper',
    roleColor: 'orange',
    status: 'Inactive',
    contact: '075-5555555',
    lastLogin: '2 days ago',
    avatarColor: 'bg-orange-200',
  },
  {
    id: 4,
    employeeId: '#EMP004',
    name: 'Anura Fernando',
    nic: '851234570V',
    role: 'Manager',
    roleColor: 'purple',
    status: 'Active',
    contact: '076-1111111',
    lastLogin: 'Today, 10 AM',
    avatarColor: 'bg-purple-200',
  },
    
  
];


export function StaffTable({ staffMembers = defaultStaffMembers, onEdit, onDelete }: StaffTableProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const getRoleBadgeClasses = (color: string) => {
    const colorMap: Record<string, string> = {
      blue: 'bg-blue-100 text-blue-700',
      green: 'bg-green-100 text-green-700',
      orange: 'bg-orange-100 text-orange-800',
    };
    return colorMap[color] || 'bg-gray-100 text-gray-700';
  };

  return (
    <>
      <div className="border border-orange-100 rounded-lg overflow-hidden bg-white">
        {/* Table Header */}
        <div className="rounded-t-lg bg-orange-50 p-4 flex items-center">
          <h4 className="font-semibold text-orange-700">Staff Members</h4>
        </div>
        {/* Table */}
        <div className="p-4 overflow-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-orange-50 text-orange-700">
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Employee ID</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Employee</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">NIC</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Role</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Contact</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Last Login</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Status</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Actions</th>
              </tr>
            </thead>
            <tbody>
              {staffMembers.map((member) => (
                <tr key={member.id} className="border-b border-orange-100 hover:bg-[#FFF7F0] transition-colors">
                  {/* Employee ID */}
                  <td className="py-3 px-4 text-gray-800 font-medium">{member.employeeId}</td>
                  {/* Employee Name + Avatar */}
                  <td className="py-3 px-4 text-gray-900 flex items-center gap-3">
                    <Avatar className={`size-8 ${member.avatarColor || 'bg-gray-200'}`}> 
                      <AvatarFallback>{member.name.split(' ').map(n => n[0]).join('').slice(0,2)}</AvatarFallback>
                    </Avatar>
                    <span>{member.name}</span>
                  </td>
                    <td className="py-3 px-4 text-gray-600">{member.nic}</td>
                  <td className="py-3 px-4">
                    <Badge className={`${getRoleBadgeClasses(member.roleColor)} px-3 py-1`}>
                      {member.role}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-gray-700">{member.contact}</td>
                  <td className="py-3 px-4 text-gray-500">{member.lastLogin}</td>
                  {/* Status Badge */}
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center gap-2 ${member.status === 'Active' ? 'text-green-700' : 'text-gray-500'}`}>
                      <span className={`w-2 h-2 rounded-full ${member.status === 'Active' ? 'bg-green-500' : 'bg-gray-400'}`}></span>
                      {member.status}
                    </span>
                  </td>
                  {/* Actions */}
                  <td className="py-3 px-4 flex gap-2">
                    <button 
                      className="p-2 rounded hover:bg-orange-100 text-orange-500"
                      onClick={() => onEdit && onEdit(member)}
                      title="Edit user"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button 
                      className="p-2 rounded hover:bg-orange-100 text-red-500"
                      onClick={() => onDelete && onDelete(member)}
                      title="Delete user"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {/* Add User Modal */}
      <AddUserModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  );
}
