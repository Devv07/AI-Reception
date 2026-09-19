import { ReceptionState } from '../types/reception';

export type AvatarState =
  | 'idle'
  | 'visitor_detected'
  | 'greeting'
  | 'listening'
  | 'thinking'
  | 'speaking'
  | 'visitor_left';

export function toAvatarState(state: ReceptionState): AvatarState {
  switch (state) {
    case 'VISITOR_DETECTED':
      return 'visitor_detected';
    case 'GREETING':
      return 'greeting';
    case 'LISTENING':
      return 'listening';
    case 'THINKING':
      return 'thinking';
    case 'SPEAKING':
      return 'speaking';
    case 'COMPLETED':
      return 'visitor_left';
    case 'IDLE':
    case 'ACTION_APPOINTMENT':
    case 'ACTION_TICKET':
    case 'HANDOFF':
    case 'UNKNOWN_QUESTION':
    default:
      return 'idle';
  }
}
