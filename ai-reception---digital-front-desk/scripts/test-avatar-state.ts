import assert from 'node:assert/strict';
import { toAvatarState } from '../src/services/avatarState';

const expected = {
  IDLE: 'idle',
  VISITOR_DETECTED: 'visitor_detected',
  GREETING: 'greeting',
  LISTENING: 'listening',
  THINKING: 'thinking',
  SPEAKING: 'speaking',
  COMPLETED: 'visitor_left',
  ACTION_APPOINTMENT: 'idle',
  ACTION_TICKET: 'idle',
  HANDOFF: 'idle',
  UNKNOWN_QUESTION: 'idle',
} as const;

for (const [receptionState, avatarState] of Object.entries(expected)) {
  assert.equal(toAvatarState(receptionState as keyof typeof expected), avatarState);
}

console.log(`Verified ${Object.keys(expected).length} reception/avatar state mappings.`);