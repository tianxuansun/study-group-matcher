variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "sgm"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnets" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  type    = list(string)
  default = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_name" {
  type    = string
  default = "sgm"
}

variable "db_username" {
  type    = string
  default = "sgm_user"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "desired_count" {
  type    = number
  default = 1
}

# Set after you push to ECR (e.g., 123456789012.dkr.ecr.us-east-1.amazonaws.com/sgm-api:latest)
variable "container_image" {
  type = string
}
