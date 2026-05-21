/**
 * supabase.ts
 * Singleton Supabase JS client — mirrors utils/db.py's singleton pattern.
 * Uses VITE_* env vars (safe for browser exposure — anon key only).
 */
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('❌ Supabase credentials missing from frontend/.env')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
