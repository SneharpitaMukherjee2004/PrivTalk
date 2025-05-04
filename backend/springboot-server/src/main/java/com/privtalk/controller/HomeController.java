package com.privtalk.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Autowired;
import com.privtalk.model.User;
import com.privtalk.service.EmailService;
@RestController
public class HomeController {

    @GetMapping("/login")
    public String home() {
        return "login";
    }
    
    @Autowired
    private EmailService emailService;
    
    @PostMapping("/register")
    public String registerUser(@ModelAttribute User user) {
        // Your logic to save user
        emailService.sendVerificationEmail(user.getEmail());
        return "redirect:/login?emailSent=true";
    }



}

