package com.privtalk.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;

import com.privtalk.model.User;
import com.privtalk.service.UserService;
import com.privtalk.service.EmailService;
@RestController
public class HomeController {

    @GetMapping("/login")
    public String home() {
        return "login";
    }
    
    @Autowired
    private EmailService emailService;
    


    @PostMapping("/verify")
    public ResponseEntity<?> verifyEmail(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        emailService.sendVerificationEmail(email);
        return ResponseEntity.ok().body(Map.of("message", "Verification email sent"));
    }
}







