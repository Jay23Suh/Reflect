import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL
const SUPABASE_ANON_KEY = process.env.REACT_APP_SUPABASE_ANON_KEY
const missingConfig = [
  !SUPABASE_URL && 'REACT_APP_SUPABASE_URL',
  !SUPABASE_ANON_KEY && 'REACT_APP_SUPABASE_ANON_KEY',
].filter(Boolean)

// Must capture BEFORE createClient, which processes and clears the hash
export const isPasswordRecovery = window.location.hash.includes('type=recovery')
export const supabaseConfigError = missingConfig.length > 0
  ? `Missing Supabase config: ${missingConfig.join(', ')}. Add them to /ground-app/.env.local and restart the dev server.`
  : null

export const supabase = supabaseConfigError
  ? null
  : createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
