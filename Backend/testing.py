from supabase import create_client

SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFwdXlwdHhsaHlubWx2ZXRlcGFoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMxNzQwMiwiZXhwIjoyMDc2ODkzNDAyfQ.mXqjdeRRJvZBhwbZNxtp6x-YylykL4Yq7azG9QYP_3c"
SUPABASE_URL="https://qpuyptxlhynmlvetepah.supabase.co"  
OWNER_EMAIL="aadithyanayakv07@gmail.com"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

res = supabase.auth.sign_in_with_password({
    "email": "aadithyanayakv07@gmail.com",
    "password": "123456"
})
token = res.session.access_token
# print(res)
print(token)
