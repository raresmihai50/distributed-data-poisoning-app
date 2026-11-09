package ro.ddpa.dto;

public record PoisonResponse(
    String original_label,
    double original_confidence,
    String poisoned_label,
    double poisoned_confidence,
    double epsilon,
    int steps,
    String poisoned_image_base64
) {}