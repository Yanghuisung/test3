import { createContext, useContext, useEffect, useState, type ReactNode, type ReactElement } from 'react';
import { listMembers } from '../utils/db';
import { useToast } from './ToastContext';
import type { Member } from '../types';

interface CurrentUserCtx {
  currentMemberId: string;
  currentMember: Member | undefined;
  members: Member[];
  setCurrentMemberId: (id: string) => void;
  refreshMembers: () => void;
}

const CurrentUserContext = createContext<CurrentUserCtx>({
  currentMemberId: '',
  currentMember: undefined,
  members: [],
  setCurrentMemberId: () => {},
  refreshMembers: () => {},
});

export const useCurrentUser = () => useContext(CurrentUserContext);

export const CurrentUserProvider = ({ children }: { children: ReactNode }): ReactElement => {
  const { showToast } = useToast();
  const [currentMemberId, setCurrentMemberIdState] = useState<string>(
    () => localStorage.getItem('wl_current_user') ?? ''
  );
  const [members, setMembers] = useState<Member[]>([]);

  const refreshMembers = () => {
    listMembers()
      .then(setMembers)
      .catch((err) => { console.error(err); showToast('구성원 목록을 불러오는 중 오류가 발생했습니다.', 'error'); });
  };

  useEffect(() => { refreshMembers(); }, []);

  const setCurrentMemberId = (id: string) => {
    localStorage.setItem('wl_current_user', id);
    setCurrentMemberIdState(id);
  };

  const currentMember = members.find((m) => m.id === currentMemberId);

  return (
    <CurrentUserContext.Provider value={{ currentMemberId, currentMember, members, setCurrentMemberId, refreshMembers }}>
      {children}
    </CurrentUserContext.Provider>
  );
};
