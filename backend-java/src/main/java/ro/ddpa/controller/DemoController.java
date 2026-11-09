package ro.ddpa.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.multipart.MultipartFile;

import ro.ddpa.dto.PoisonResponse;

@RestController
@RequestMapping("/api/demo")
@CrossOrigin(origins = "*") // Permite apelurile de la viitorul frontend Svelte
public class DemoController {

    private final RestClient restClient;

    public DemoController(@Value("${ai.worker.url}") String workerUrl) {
        // Configurăm clientul modern REST către Python (port 8000)
        this.restClient = RestClient.builder()
                .baseUrl(workerUrl)
                .build();
    }

    @PostMapping(value = "/protect", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public PoisonResponse protectImage(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "epsilon", defaultValue = "0.05") double epsilon,
            @RequestParam(value = "steps", defaultValue = "10") int steps
    ) {
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", file.getResource());
        body.add("epsilon", epsilon);
        body.add("steps", steps);

        // Trimite imaginea la Python și mapează automat răspunsul pe recordul PoisonResponse
        return restClient.post()
                .uri("/poison")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(body)
                .retrieve()
                .body(PoisonResponse.class);
    }

        @GetMapping("/health")
    public String healthCheck() {
        try {
            // Trimite un mic semnal de salut către Python (port 8000)
            String pythonStatus = restClient.get()
                    .uri("/")
                    .retrieve()
                    .body(String.class);

            return "✅ CONEXIUNE REUȘITĂ! Java (8080) comunică perfect cu Python (8000).";
        } catch (Exception e) {
            return "⚠️ Java funcționează, dar nu poate contacta Python (asigură-te că rulezi uvicorn pe portul 8000). Eroare: " + e.getMessage();
        }
    }
}