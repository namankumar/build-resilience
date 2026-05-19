const API_URL = 'http://localhost:8000';

export async function createReflection(text, mood = null) {
  const resp = await fetch(`${API_URL}/reflections`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, mood })
  });
  if (!resp.ok) throw new Error('Failed to create reflection');
  return resp.json();
}

export async function getReframe(reflectionId) {
  const resp = await fetch(`${API_URL}/reframe/${reflectionId}`);
  if (!resp.ok) throw new Error('Failed to get reframe');
  return resp.json();
}

export async function recordWin(reflectionId, win) {
  const resp = await fetch(`${API_URL}/wins`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reflection_id: reflectionId, win })
  });
  if (!resp.ok) throw new Error('Failed to record win');
  return resp.json();
}

export async function getStreak() {
  const resp = await fetch(`${API_URL}/streak`);
  if (!resp.ok) throw new Error('Failed to get streak');
  return (await resp.json()).count;
}

export async function getWinrack() {
  const resp = await fetch(`${API_URL}/winrack`);
  if (!resp.ok) throw new Error('Failed to get win rack');
  return (await resp.json()).wins;
}
