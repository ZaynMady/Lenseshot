import {createClient} from '@supabase/supabase-js'

export default function AccountPage(){
    const supabaseUrl = import.meta.env.VITE_SUPABASE_PROJECT_URL;
    const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
    const supabase = createClient(supabaseUrl, supabaseKey);

    return (
        <div className="p-6 text-white">
            <h1 className="text-2xl font-bold mb-4">Account Page</h1>
            <p>Manage your account settings and preferences here.</p>
            <button className="mt-4 px-4 py-2 bg-red-600 rounded hover:bg-red-700"
            onClick={async () => {
                const { error } = await supabase.auth.signOut();
                if (error) console.error('Error signing out:', error.message);
                else window.location.href = '/Auth'; // Redirect to login page after sign out
            }}>
                Sign Out
            </button>
        </div>

    );


}