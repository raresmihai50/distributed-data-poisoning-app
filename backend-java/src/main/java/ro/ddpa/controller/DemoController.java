package ro.ddpa.controller;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
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
@CrossOrigin(origins = "*")
public class DemoController {

    private final RestClient restClient;

    public DemoController(@Value("${ai.worker.url}") String workerUrl) {
        // Folosim SimpleClientHttpRequestFactory (HTTP/1.1 standard) pentru a evita
        // headerul "Upgrade: h2c" (HTTP/2) pe care Uvicorn/FastAPI îl respinge.
        this.restClient = RestClient.builder()
                .baseUrl(workerUrl)
                .requestFactory(new SimpleClientHttpRequestFactory())
                .build();
    }

    @PostMapping(value = "/protect", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public PoisonResponse protectImage(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "epsilon", defaultValue = "0.05") double epsilon,
            @RequestParam(value = "steps", defaultValue = "10") int steps
    ) throws IOException {

        // 1. Împachetăm octeții fișierului și îi garantăm un nume explicit (necesar pentru FastAPI)
        ByteArrayResource fileResource = new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return (file.getOriginalFilename() != null && !file.getOriginalFilename().isBlank())
                        ? file.getOriginalFilename()
                        : "image.png";
            }
        };

        // 2. Setăm antetul corect de imagine (ex: image/png, image/jpeg)
        HttpHeaders fileHeaders = new HttpHeaders();
        fileHeaders.setContentType(file.getContentType() != null
                ? MediaType.parseMediaType(file.getContentType())
                : MediaType.IMAGE_PNG);
        HttpEntity<ByteArrayResource> fileEntity = new HttpEntity<>(fileResource, fileHeaders);

        // 3. Construim corpul multipart trimis către Python (valorile ca String pentru form-data)
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", fileEntity);
        body.add("epsilon", String.valueOf(epsilon));
        body.add("steps", String.valueOf(steps));

        // 4. Apelăm Python pe portul 8000 prin HTTP/1.1 multipart/form-data
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
            restClient.get().uri("/").retrieve().body(String.class);
            return "✅ CONEXIUNE REUȘITĂ! Java (8080) comunică cu Python (8000).";
        } catch (Exception e) {
            return "⚠️ Eroare la contactarea Python: " + e.getMessage();
        }
    }
}
