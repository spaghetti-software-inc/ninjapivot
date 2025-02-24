# autoninja


https://github.com/user-attachments/assets/7f688221-ad35-4b92-bf74-d5bc03d66613




## Front-End
Below is a concise set of **requirements and design specifications** for the Ninjapivot front-end MVP, using **React + Vite** for the application scaffolding and **TailwindCSS** for styling.

---

## 1. Overall Objectives
1. **Minimal friction**: Users should be able to upload a CSV file and receive a PDF report with minimal extra steps.  
2. **Anonymous usage**: No login or account creation is required for the free version.  
3. **Progress Visibility**: Users should see basic progress updates while their file is analyzed.  
4. **Report Delivery**: Once the analysis is complete, the user can view and download the PDF report directly on the page.

---

## 2. Page Structure
1. **Landing Page** (Upload Page)  
   - **Header/Branding**: A simple header or banner with the service name (“Ninjapivot”).  
   - **CSV Upload Section**:  
     - Drag-and-drop area (optional for MVP) or a file input button.  
     - Constraints/tips (e.g., “Max 10,000 rows, 100 columns”).  
     - A button to “Upload & Analyze.”  
   - **Footer (optional)**: Very minimal for the MVP—maybe a copyright or version number.

2. **Results Page** (Analysis + Report Display)  
   - **Progress Indicator**: Displays while the backend processes the file.  
     - Could be a simple spinner or progress bar.  
     - A textual status update, e.g., “Analyzing data (step 2/5).”  
   - **Report Preview**:  
     - Embed or display the generated PDF in an inline frame (iFrame) once ready.  
     - A “Download Report” button to save the PDF locally.  
   - **Back / New Analysis** Option: A button or link to return to the landing page for another upload.

---

## 3. User Flow
1. **User Arrives** → Sees a simple landing page with instructions to upload a CSV.  
2. **User Uploads CSV** → Immediately or upon clicking “Analyze,” the file is sent to the backend.  
3. **Analysis in Progress** → User is redirected to the Results page with a spinner or progress bar.  
   - The front-end polls the backend (e.g., every 3–5 seconds) for status updates.  
4. **Analysis Complete** → PDF is generated, and the front-end displays a preview plus a download button.  
5. **User Downloads Report** → Optionally, user returns to the landing page to upload a new CSV.

---

## 4. Visual and UX Design
1. **Look and Feel**  
   - Utilize **TailwindCSS** utility classes for rapid styling.  
   - Maintain a **clean, modern look** with minimal clutter.  
   - Use neutral or subtle brand colors.  
2. **Responsiveness**  
   - The layout should adapt to mobile, tablet, and desktop views.  
   - Upload button/area should be large enough for touch devices.  
   - PDF preview area should be scrollable or adaptable on smaller screens.  
3. **Error Handling and Messaging**  
   - If the file exceeds row/column limits, display a clear error message.  
   - If the backend returns an error, show a user-friendly message (“We encountered an error analyzing your data. Please try again.”).  
4. **Accessibility**  
   - Provide alt text for images/icons (if any).  
   - Ensure color contrast is sufficient for text and backgrounds.

---

## 5. Technical Implementation Details
1. **Front-End Framework**: **React** bootstrapped with **Vite**.  
   - **File Upload**: Use an `<input type="file" />` or a drag-and-drop library.  
   - Manage state (e.g., selected file, analysis status) in React’s local state or a simple global store.  
2. **HTTP Requests**:  
   - **Upload**: POST `/upload` → sends the CSV file (FormData) to the FastAPI backend.  
   - **Status Polling**: GET `/status/{job_id}` → returns JSON with progress info.  
   - **PDF Retrieval**: Once complete, the PDF is served at `/result/{job_id}`.  
3. **Progress Display**:  
   - The front-end sets an interval (e.g., `setInterval(...)`) to call the status endpoint.  
   - Upon receiving updated progress, the UI re-renders the progress indicator.  
   - When status indicates “complete,” front-end fetches the PDF or displays the iFrame.  
4. **PDF Viewing**:  
   - Use an `<iframe>` or a specialized PDF viewer component to show the generated PDF inline.  
   - Provide a “Download” button that links directly to `/result/{job_id}?download=true` (or similar).

---

## 6. Potential Enhancements (Beyond MVP)
1. **Drag-and-Drop**: Enhance usability instead of relying on file input.  
2. **WebSocket Notifications**: Real-time progress updates without polling.  
3. **User Options**: Let users specify certain parameters (e.g., significance level) before analysis.  
4. **Template/Styling Options**: In the future, users could pick from different PDF report styles.  
5. **Multi-Language**: Internationalize the UI and report text.

---

### Summary

The MVP front-end design centers on a **two-page flow** (Upload Page → Results Page) with minimal navigation and a simple, clean UI. TailwindCSS provides a modern and responsive design foundation, while React with Vite keeps the development experience fast. Users can upload CSVs anonymously, watch progress via polling, then view and download a generated PDF report. This approach meets the core requirement of delivering an automated statistician experience with minimal user friction.
