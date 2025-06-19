-- Resilience App Database Schema - CORRECTED VERSION
-- Run this in Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE reflection_mood AS ENUM ('very_negative', 'negative', 'neutral', 'positive', 'very_positive');
CREATE TYPE win_category AS ENUM (
    'movement', 'mindfulness', 'connection', 'self-care', 'productivity'
);

-- 1. User Profiles Table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Reflections Table (CORRECTED - added mood_emoji and mood_intensity)
CREATE TABLE IF NOT EXISTS public.reflections (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    content TEXT NOT NULL,
    mood reflection_mood,
    mood_emoji TEXT,
    mood_intensity INTEGER CHECK (mood_intensity >= 1 AND mood_intensity <= 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Reframes Table (CORRECTED - added new fields for API compatibility)
CREATE TABLE IF NOT EXISTS public.reframes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    reflection_id UUID REFERENCES public.reflections(id) ON DELETE CASCADE,
    original_thought TEXT NOT NULL,
    reframed_thought TEXT NOT NULL,
    ai_generated BOOLEAN DEFAULT FALSE,
    is_helpful BOOLEAN,
    content TEXT,
    ai_model_used TEXT,
    saved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Wins Table (CORRECTED - added missing columns)
CREATE TABLE IF NOT EXISTS public.wins (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category win_category DEFAULT 'other',
    estimated_minutes INTEGER,
    is_custom BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Win Completions Table (CORRECTED - added mood_after and reflection_id)
CREATE TABLE IF NOT EXISTS public.win_completions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    win_id UUID REFERENCES public.wins(id) ON DELETE CASCADE NOT NULL,
    reflection_id UUID REFERENCES public.reflections(id) ON DELETE CASCADE,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    mood_after INTEGER CHECK (mood_after >= 1 AND mood_after <= 10)
);

-- 6. Streaks Table (unchanged - this was correct)
CREATE TABLE IF NOT EXISTS public.streaks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    streak_type TEXT DEFAULT 'daily',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, streak_type)
);

-- 7. Chat Sessions Table (CORRECTED - this was missing entirely)
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    reflection_id UUID REFERENCES public.reflections(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'active',
    current_mode TEXT DEFAULT 'listen',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- 8. Chat Messages Table (CORRECTED - updated structure for new API)
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    session_id UUID REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    role TEXT,
    ai_model_used TEXT,
    mood_analysis JSONB,
    is_user_message BOOLEAN DEFAULT TRUE,
    ai_model TEXT,
    conversation_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_reflections_user_id ON public.reflections(user_id);
CREATE INDEX IF NOT EXISTS idx_reflections_created_at ON public.reflections(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reflections_mood ON public.reflections(mood_intensity);

CREATE INDEX IF NOT EXISTS idx_reframes_user_id ON public.reframes(user_id);
CREATE INDEX IF NOT EXISTS idx_reframes_reflection_id ON public.reframes(reflection_id);

CREATE INDEX IF NOT EXISTS idx_wins_user_id ON public.wins(user_id);
CREATE INDEX IF NOT EXISTS idx_wins_completed ON public.wins(is_completed);
CREATE INDEX IF NOT EXISTS idx_wins_usage ON public.wins(usage_count, last_used_at);

CREATE INDEX IF NOT EXISTS idx_win_completions_user_id ON public.win_completions(user_id);
CREATE INDEX IF NOT EXISTS idx_win_completions_date ON public.win_completions(completed_at DESC);

CREATE INDEX IF NOT EXISTS idx_streaks_user_id ON public.streaks(user_id);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON public.chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation ON public.chat_messages(conversation_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reflections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reframes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wins ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.win_completions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.streaks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies (users can only access their own data)

-- User Profiles Policies
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Reflections Policies
CREATE POLICY "Users can view own reflections" ON public.reflections
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own reflections" ON public.reflections
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own reflections" ON public.reflections
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own reflections" ON public.reflections
    FOR DELETE USING (auth.uid() = user_id);

-- Reframes Policies
CREATE POLICY "Users can view own reframes" ON public.reframes
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own reframes" ON public.reframes
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own reframes" ON public.reframes
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own reframes" ON public.reframes
    FOR DELETE USING (auth.uid() = user_id);

-- Wins Policies
CREATE POLICY "Users can view own wins" ON public.wins
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own wins" ON public.wins
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own wins" ON public.wins
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own wins" ON public.wins
    FOR DELETE USING (auth.uid() = user_id);

-- Win Completions Policies
CREATE POLICY "Users can view own win completions" ON public.win_completions
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own win completions" ON public.win_completions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Streaks Policies
CREATE POLICY "Users can view own streaks" ON public.streaks
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own streaks" ON public.streaks
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own streaks" ON public.streaks
    FOR UPDATE USING (auth.uid() = user_id);

-- Chat Sessions Policies
CREATE POLICY "Users can manage own chat sessions" ON public.chat_sessions
    FOR ALL USING (auth.uid() = user_id);

-- Chat Messages Policies
CREATE POLICY "Users can view own chat messages" ON public.chat_messages
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own chat messages" ON public.chat_messages
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at columns
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_reflections_updated_at
    BEFORE UPDATE ON public.reflections
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_reframes_updated_at
    BEFORE UPDATE ON public.reframes
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_wins_updated_at
    BEFORE UPDATE ON public.wins
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_streaks_updated_at
    BEFORE UPDATE ON public.streaks
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at
    BEFORE UPDATE ON public.chat_sessions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();