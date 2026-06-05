import { NextResponse } from 'next/server';

export async function GET() {
  // In a real application, this would fetch real-time data from the Python Orchestrator
  // or a shared Redis cache/database. For now, it returns mock data.
  
  const systemStatus = {
    isOnline: true,
    nodes: {
      orchestrator: 'online',
      vision: 'online',
      websurfer: 'online',
      computer: 'warning'
    },
    memory: {
      sqlite_size: '45 MB',
      neo4j_nodes: 128,
      chromadb_vectors: 1024,
      last_sync: new Date().toISOString()
    },
    sandbox: {
      blocked_commands: 0,
      pending_approvals: 2
    }
  };

  return NextResponse.json(systemStatus);
}
