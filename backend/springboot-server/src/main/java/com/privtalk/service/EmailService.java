package com.privtalk.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class EmailService {

    @Autowired
    private RestTemplate restTemplate;

    public void sendVerificationEmail(String email) {
        String url = "http://localhost:8000/send-verification";  // FastAPI endpoint

        Map<String, String> body = new HashMap<>();
        body.put("email", email);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, String>> request = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            System.out.println("Response from FastAPI: " + response.getBody());
        } catch (Exception e) {
            System.err.println("Email verification failed: " + e.getMessage());
        }
    }
}
