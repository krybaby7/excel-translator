-- Excel Translator - Supabase Database Schema

-- Create translation_jobs table for tracking translation progress
CREATE TABLE IF NOT EXISTS translation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Job metadata
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'complete', 'error')),

    -- File information
    original_filename VARCHAR(255) NOT NULL,
    input_file_path VARCHAR(500),
    output_file_path VARCHAR(500),
    file_size BIGINT,

    -- Translation settings
    source_lang VARCHAR(10) NOT NULL DEFAULT 'fr',
    target_lang VARCHAR(10) NOT NULL DEFAULT 'en',

    -- Progress tracking
    current_cell INTEGER DEFAULT 0,
    total_cells INTEGER DEFAULT 0,
    progress_message TEXT DEFAULT 'Starting translation...',
    progress_percentage INTEGER DEFAULT 0,

    -- Error handling
    error_message TEXT,

    -- Cleanup tracking
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours')
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_translation_jobs_status ON translation_jobs(status);
CREATE INDEX IF NOT EXISTS idx_translation_jobs_created_at ON translation_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_translation_jobs_expires_at ON translation_jobs(expires_at);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_translation_jobs_updated_at ON translation_jobs;
CREATE TRIGGER update_translation_jobs_updated_at
    BEFORE UPDATE ON translation_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to automatically update progress_percentage
CREATE OR REPLACE FUNCTION update_progress_percentage()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.total_cells > 0 THEN
        NEW.progress_percentage = ROUND((NEW.current_cell::NUMERIC / NEW.total_cells::NUMERIC) * 100);
    ELSE
        NEW.progress_percentage = 0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-calculate progress_percentage
DROP TRIGGER IF EXISTS calculate_progress_percentage ON translation_jobs;
CREATE TRIGGER calculate_progress_percentage
    BEFORE INSERT OR UPDATE OF current_cell, total_cells ON translation_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_progress_percentage();

-- Create function to clean up old jobs (run via cron job)
CREATE OR REPLACE FUNCTION cleanup_expired_jobs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete jobs that have expired
    DELETE FROM translation_jobs
    WHERE expires_at < NOW()
    RETURNING COUNT(*) INTO deleted_count;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security (RLS)
ALTER TABLE translation_jobs ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (you can restrict this later with authentication)
CREATE POLICY "Allow all operations on translation_jobs"
ON translation_jobs
FOR ALL
TO public
USING (true)
WITH CHECK (true);

-- Optional: If you add authentication later, replace above policy with:
-- CREATE POLICY "Users can view their own jobs"
-- ON translation_jobs FOR SELECT
-- TO authenticated
-- USING (auth.uid() = user_id);

-- Create a view for active jobs (jobs not expired or errored)
CREATE OR REPLACE VIEW active_translation_jobs AS
SELECT
    id,
    created_at,
    updated_at,
    status,
    original_filename,
    source_lang,
    target_lang,
    current_cell,
    total_cells,
    progress_percentage,
    progress_message
FROM translation_jobs
WHERE status IN ('pending', 'processing')
AND expires_at > NOW()
ORDER BY created_at DESC;

-- Grant permissions
GRANT ALL ON translation_jobs TO authenticated, anon;
GRANT ALL ON active_translation_jobs TO authenticated, anon;

-- Insert a test record (optional - you can delete this)
-- INSERT INTO translation_jobs (original_filename, source_lang, target_lang, status, progress_message)
-- VALUES ('test.xlsx', 'fr', 'en', 'pending', 'Test job created');

COMMENT ON TABLE translation_jobs IS 'Stores translation job metadata and progress tracking';
COMMENT ON COLUMN translation_jobs.expires_at IS 'Jobs expire after 24 hours and should be cleaned up';
COMMENT ON FUNCTION cleanup_expired_jobs() IS 'Call this function periodically to remove old jobs and their files';
