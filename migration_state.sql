-- Migration to add state persistence columns to users table

-- Add 'state' column
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS state text DEFAULT 'start';

-- Add 'data' column to store conversation data (JSON)
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS data jsonb DEFAULT '{}'::jsonb;

-- Comment
COMMENT ON COLUMN public.users.state IS 'Current conversation state of the user';
COMMENT ON COLUMN public.users.data IS 'Temporary conversation data';
