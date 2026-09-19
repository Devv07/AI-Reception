import React, { useEffect, useRef } from 'react';
import { ReceptionState } from '../../types/reception';
import { toAvatarState } from '../../services/avatarState';
import { AIOrb } from './AIOrb';

interface VRMAvatarProps {
  state: ReceptionState;
  onClick?: () => void;
}

const AVATAR_URL = import.meta.env.VITE_AVATAR_URL as string | undefined;

export const VRMAvatar: React.FC<VRMAvatarProps> = ({ state, onClick }) => {
  const frameRef = useRef<HTMLIFrameElement>(null);
  const avatarState = toAvatarState(state);

  useEffect(() => {
    frameRef.current?.contentWindow?.postMessage({ type: 'ai-reception-avatar-state', state: avatarState }, '*');
  }, [avatarState]);

  if (!AVATAR_URL) {
    return <AIOrb state={state} onClick={onClick} />;
  }

  return (
    <div className="relative w-full max-w-3xl aspect-[4/3] min-h-[280px] overflow-hidden rounded-3xl border border-cyan-500/20 bg-slate-950/40 shadow-2xl">
      <iframe
        ref={frameRef}
        title="AI Receptionist avatar"
        src={AVATAR_URL}
        onLoad={() => frameRef.current?.contentWindow?.postMessage({ type: 'ai-reception-avatar-state', state: avatarState }, '*')}
        className="h-full w-full border-0"
      />
    </div>
  );
};
