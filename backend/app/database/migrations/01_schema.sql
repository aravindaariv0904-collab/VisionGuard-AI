-- VisionGuard AI - Database Migration Schema
-- Target: Supabase PostgreSQL (auth, public, storage schemas)

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

---------------------------------------------------
-- 1. Create Tables
---------------------------------------------------

-- Users profiles table (linked to auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    role TEXT NOT NULL DEFAULT 'User' CHECK (role IN ('User', 'Admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Model versions tracking table
CREATE TABLE IF NOT EXISTS public.model_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL UNIQUE,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT true,
    accuracy DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Predictions table
CREATE TABLE IF NOT EXISTS public.predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    original_image_url TEXT NOT NULL,
    prediction TEXT NOT NULL CHECK (prediction IN ('Real', 'AI Generated')),
    confidence DOUBLE PRECISION NOT NULL, -- e.g. 97.8
    processing_time DOUBLE PRECISION NOT NULL, -- e.g. 0.42 (seconds)
    model_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Heatmaps table (linked to predictions)
CREATE TABLE IF NOT EXISTS public.heatmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL REFERENCES public.predictions(id) ON DELETE CASCADE UNIQUE,
    heatmap_url TEXT NOT NULL,
    overlay_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Uploads table (file metadata)
CREATE TABLE IF NOT EXISTS public.uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    file_name TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Batch jobs table
CREATE TABLE IF NOT EXISTS public.batch_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    total_images INTEGER NOT NULL DEFAULT 0,
    processed_images INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Batch results table
CREATE TABLE IF NOT EXISTS public.batch_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES public.batch_jobs(id) ON DELETE CASCADE,
    prediction_id UUID REFERENCES public.predictions(id) ON DELETE SET NULL,
    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILED')),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Analytics metrics table
CREATE TABLE IF NOT EXISTS public.analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name TEXT NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID, -- NULL for anonymous operations
    action TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Notifications table
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    read BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

---------------------------------------------------
-- 2. Indexes for Optimization
---------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON public.predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON public.predictions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_uploads_user_id ON public.uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_user_id ON public.batch_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_batch_results_job_id ON public.batch_results(job_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON public.audit_logs(timestamp DESC);

---------------------------------------------------
-- 3. Supabase Auth sync Trigger
---------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name, role)
  VALUES (
    new.id,
    new.email,
    COALESCE(new.raw_user_meta_data->>'full_name', ''),
    'User'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to run whenever a user is inserted in auth.users
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

---------------------------------------------------
-- 4. Supabase Storage Bucket Initializations
---------------------------------------------------
-- Insert buckets into storage schema (if they don't exist)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES 
  ('original-images', 'original-images', true, 10485760, ARRAY['image/jpeg', 'image/png', 'image/webp']),
  ('heatmaps', 'heatmaps', true, 10485760, ARRAY['image/jpeg', 'image/png', 'image/webp']),
  ('reports', 'reports', true, 20971520, ARRAY['application/pdf', 'application/json']),
  ('batch-images', 'batch-images', true, 52428800, ARRAY['image/jpeg', 'image/png', 'image/webp', 'application/zip']),
  ('avatars', 'avatars', true, 2097152, ARRAY['image/jpeg', 'image/png', 'image/webp'])
ON CONFLICT (id) DO NOTHING;

---------------------------------------------------
-- 5. Row Level Security (RLS) Policies
---------------------------------------------------

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.heatmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.batch_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.batch_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- USERS Table Policies
CREATE POLICY "Users can view their own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile name" ON public.users
    FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

CREATE POLICY "Admins have full access on profiles" ON public.users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE public.users.id = auth.uid() AND public.users.role = 'Admin'
        )
    );

-- PREDICTIONS Table Policies
CREATE POLICY "Users can view their own predictions" ON public.predictions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own predictions" ON public.predictions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins have full access on predictions" ON public.predictions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE public.users.id = auth.uid() AND public.users.role = 'Admin'
        )
    );

-- HEATMAPS Table Policies (Visible if predictions is visible)
CREATE POLICY "Users can view heatmaps linked to their predictions" ON public.heatmaps
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.predictions
            WHERE public.predictions.id = heatmap.prediction_id AND public.predictions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert heatmaps" ON public.heatmaps
    FOR INSERT WITH CHECK (true);

-- UPLOADS Table Policies
CREATE POLICY "Users can view their own uploads" ON public.uploads
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own uploads" ON public.uploads
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- BATCH JOBS Table Policies
CREATE POLICY "Users can view their own batch jobs" ON public.batch_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert/update their own batch jobs" ON public.batch_jobs
    FOR ALL USING (auth.uid() = user_id);

-- BATCH RESULTS Table Policies
CREATE POLICY "Users can view batch results linked to their jobs" ON public.batch_results
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.batch_jobs
            WHERE public.batch_jobs.id = batch_results.job_id AND public.batch_jobs.user_id = auth.uid()
        )
    );

-- NOTIFICATIONS Table Policies
CREATE POLICY "Users can view their own notifications" ON public.notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update read status" ON public.notifications
    FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- MODEL VERSIONS Table Policies
CREATE POLICY "Anyone can view active model versions" ON public.model_versions
    FOR SELECT USING (true);

-- ANALYTICS Table Policies (Admin Only)
CREATE POLICY "Admins can manage analytics" ON public.analytics
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE public.users.id = auth.uid() AND public.users.role = 'Admin'
        )
    );

-- AUDIT LOGS Table Policies (Admin Only)
CREATE POLICY "Admins can view audit logs" ON public.audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE public.users.id = auth.uid() AND public.users.role = 'Admin'
        )
    );

---------------------------------------------------
-- 6. Insert Seed Data
---------------------------------------------------
INSERT INTO public.model_versions (version, description, active, accuracy)
VALUES ('6630a40', 'Trained EfficientNet-B0 Model', true, 97.17)
ON CONFLICT (version) DO NOTHING;
