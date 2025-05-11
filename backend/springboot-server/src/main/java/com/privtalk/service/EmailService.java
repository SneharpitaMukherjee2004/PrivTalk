package com.privtalk.service;

import com.privtalk.model.VerificationToken;
import com.privtalk.repository.VerificationTokenRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
public class EmailService {

    @Autowired
    private VerificationTokenRepository tokenRepository;
    public void sendVerificationEmail(String email) {
        try {
        // Prepare request body: only the email field
        Map<String, String> payload = new HashMap<>();
        payload.put("email", email);  // Match FastAPI's model

        // Set headers
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        // Build HTTP request
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(payload, headers);

        // Send to FastAPI
        RestTemplate restTemplate = new RestTemplate();
        String apiUrl = "http://localhost:1000/send-verification";
        ResponseEntity<String> response = restTemplate.postForEntity(apiUrl, entity, String.class);

        System.out.println("Email API Response: " + response.getBody());

    } catch (Exception e) {
        System.err.println("Error sending verification email: " + e.getMessage());
        e.printStackTrace();
    }
}

}
