import { createClient, SupabaseClient } from '@supabase/supabase-js'

export interface Observer {
  observer_id: number
  observer_name: string
  session_id: bigint
  login_timestamp: string
}

/**
 * ensureSessionPersisted
 * Enforces forensic audit logs before clinical commits.
 * Maps UI session to database session_log (BIGINT PK).
 */
export async function ensureSessionPersisted(observer: Observer, supabase: SupabaseClient) {
  // Check if session exists in DB
  const { data, error } = await supabase
    .from('session_log')
    .select('session_id')
    .eq('session_id', observer.session_id)
    .single()

  if (error || !data) {
    // Persist new session log
    const { error: insertError } = await supabase
      .from('session_log')
      .insert({
        session_id: observer.session_id,
        observer_name: observer.observer_name,
        login_timestamp: observer.login_timestamp
      })
    
    if (insertError) {
      console.error('Failed to persist forensic session:', insertError)
      throw new Error('Forensic session persistence failure. Clinical commit aborted.')
    }
  }
}
