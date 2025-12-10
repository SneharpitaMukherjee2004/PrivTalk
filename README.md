# PrivTalk — Secure, Token-Based Private Chatrooms
_A privacy-first communication platform built for secure one-to-one meetings._

## Overview
PrivTalk enables secure communication through unique chat tokens and private deterministic chatrooms. Users authenticate via email, manage profiles, and create or join encrypted sessions, with all media and QR assets stored in Supabase. Full cleanup—cloud meeting folder deletion, QR removal, and local temp file handling—is now fully implemented and functional.

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
- Unauthorized room join detection with alert

## Storage Architecture
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
- **Sneharpita Mukherjee** — UI/UX & Frontend  
- **Soumodeep Das** — Backend, Cloud, WebSockets  

## Future Plans
- E2E encryption  
- Video/voice calling  
- Group rooms  
- PWA & mobile app  
- Message reactions, typing indicator, and chat history export  

