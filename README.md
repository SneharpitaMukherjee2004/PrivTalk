# PrivTalk — Secure, Token-Based Private Chatrooms
_A privacy-first communication platform built for secure one-to-one meetings._

## Overview
PrivTalk enables secure communication through unique chat tokens and private deterministic chatrooms. 
Users authenticate via email, manage profiles, and create or join encrypted sessions, with all media and QR assets stored in Supabase Cloud. 
Full cleanup—cloud meeting folder deletion, QR removal, and local temp file handling—is now fully functional.

## Features
- Email verification & login (username / email)
- Secure SHA-256 password hashing
- Reset password flow
- Profile editing with cloud-stored profile picture
- Auto-generated personal QR codes
- Create and join private rooms using tokens or QR scan
- Real-time messaging via WebSockets
- Cloud media upload (images, videos, files)
- Meeting QR generation
- Automatic Supabase meeting-folder cleanup on termination
- Automatic local temp file cleanup
- Unauthorized room join deny

## Cloud Storage Architecture
```
chat-media/
 └── assets/
     ├── persons/
     │    └── <chat_token>/
     │         ├── profile/
     │         └── qrcode/
     └── meetings/
          └── <room_id>/
               ├── qrcode/
               └── data/
```

## Contributors
- **Sneharpita Mukherjee** — Planning & Logic creation, Frontend handeling, Testing & recommendation — [Github]( https://github.com/SneharpitaMukherjee2004 )
- **Soumodeep Das** — UI|UX planning, Backend handeling, Problem Solving — [Github]( https://github.com/SoumodeepDas2004 )

## Future Plans
- Video/voice calling  
- Group rooms    
- Message reactions and live chat  export  

