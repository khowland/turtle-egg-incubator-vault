import type { SupabaseClient } from '@supabase/supabase-js'

export interface Observer {
  observer_id: string  // UUID from observer table (was number, now UUID)
  observer_name: string  // matches observer.observer_name column
  session_id: bigint
  login_timestamp: string
}

/**
 * ensureSessionPersisted
 * Enforces forensic audit logs before clinical commits.
 * Maps UI session to database session_log (BIGINT PK).
 */
export async function ensureSessionPersisted(
  observer: Observer,
  supabase: SupabaseClient
): Promise<bigint> {
  // If session_id is already a real DB ID (not a pre-insert client placeholder), check it.
  if (observer.session_id > 0n) {
    const { data, error } = await supabase
      .from('session_log')
      .select('session_id')
      .eq('session_id', observer.session_id)
      .single()

    if (!error && data) {
      return observer.session_id // already persisted
    }
  }

  // Persist new session log — let DB generate session_id (GENERATED ALWAYS AS IDENTITY)
  const { data: inserted, error: insertError } = await supabase
    .from('session_log')
    .insert({
      user_name: observer.observer_name,
      login_timestamp: observer.login_timestamp,
      user_agent: navigator.userAgent,
    })
    .select('session_id')
    .single()

  if (insertError || !inserted) {
    console.error('Failed to persist forensic session:', insertError)
    throw new Error('Forensic session persistence failure. Clinical commit aborted.')
  }

  return BigInt(inserted.session_id)
}
