@extends('layouts.app')

@section('content')
    <!-- Main Content -->
    <div class="main-content">
        <section class="section">
            @if (session('success'))
                <div class="alert alert-success">
                    {{ session('success') }}
                </div>
            @endif
            <div class="section-body">
                <div class="row mt-sm-4">
                    <div class="col-12 col-md-12 col-lg-4">
                        <div class="card author-box">
                            <div class="card-body">
                                <div class="author-box-center">
                                    <img alt="image" src="assets/img/users/user-1.png" class="rounded-circle author-box-picture">
                                    <div class="clearfix"></div>
                                    <div class="author-box-name">
                                        <a href="#">Sarah Smith</a>
                                    </div>
                                    <div class="author-box-job">Web Developer</div>
                                </div>
                                <div class="text-center">
                                    <div class="author-box-description">
                                        <p>
                                            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Pariatur voluptatum alias molestias
                                            minus quod dignissimos.
                                        </p>
                                    </div>
                                    <div class="mb-2 mt-3">
                                        <div class="text-small font-weight-bold">Follow Hasan On</div>
                                    </div>
                                    <a href="#" class="btn btn-social-icon mr-1 btn-facebook">
                                        <i class="fab fa-facebook-f"></i>
                                    </a>
                                    <a href="#" class="btn btn-social-icon mr-1 btn-twitter">
                                        <i class="fab fa-twitter"></i>
                                    </a>
                                    <a href="#" class="btn btn-social-icon mr-1 btn-github">
                                        <i class="fab fa-github"></i>
                                    </a>
                                    <a href="#" class="btn btn-social-icon mr-1 btn-instagram">
                                        <i class="fab fa-instagram"></i>
                                    </a>
                                    <div class="w-100 d-sm-none"></div>
                                </div>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header">
                                <h4>Personal Details</h4>
                            </div>
                            <div class="card-body">
                                <div class="py-4">
                                    <p class="clearfix">
                        <span class="float-left">
                          Birthday
                        </span>
                                        <span class="float-right text-muted">
                          30-05-1998
                        </span>
                                    </p>
                                    <p class="clearfix">
                        <span class="float-left">
                          Phone
                        </span>
                                        <span class="float-right text-muted">
                          (0123)123456789
                        </span>
                                    </p>
                                    <p class="clearfix">
                        <span class="float-left">
                          Mail
                        </span>
                                        <span class="float-right text-muted">
                          test@example.com
                        </span>
                                    </p>
                                    <p class="clearfix">
                        <span class="float-left">
                          Facebook
                        </span>
                                        <span class="float-right text-muted">
                          <a href="#">John Deo</a>
                        </span>
                                    </p>
                                    <p class="clearfix">
                        <span class="float-left">
                          Twitter
                        </span>
                                        <span class="float-right text-muted">
                          <a href="#">@johndeo</a>
                        </span>
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header">
                                <h4>Skills</h4>
                            </div>
                            <div class="card-body">
                                <ul class="list-unstyled user-progress list-unstyled-border list-unstyled-noborder">
                                    <li class="media">
                                        <div class="media-body">
                                            <div class="media-title">Java</div>
                                        </div>
                                        <div class="media-progressbar p-t-10">
                                            <div class="progress" data-height="6">
                                                <div class="progress-bar bg-primary" data-width="70%"></div>
                                            </div>
                                        </div>
                                    </li>
                                    <li class="media">
                                        <div class="media-body">
                                            <div class="media-title">Web Design</div>
                                        </div>
                                        <div class="media-progressbar p-t-10">
                                            <div class="progress" data-height="6">
                                                <div class="progress-bar bg-warning" data-width="80%"></div>
                                            </div>
                                        </div>
                                    </li>
                                    <li class="media">
                                        <div class="media-body">
                                            <div class="media-title">Photoshop</div>
                                        </div>
                                        <div class="media-progressbar p-t-10">
                                            <div class="progress" data-height="6">
                                                <div class="progress-bar bg-green" data-width="48%"></div>
                                            </div>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-md-12 col-lg-8">
                        <div class="card">
                            <div class="padding-20">
                                <div class="tab-content tab-bordered" id="myTab3Content">
                                        <form method="POST" action="{{ route('profile.update') }}" id="profile-form" enctype="multipart/form-data" class="needs-validation">
                                            @csrf
                                            @method('PUT')
                                            <div class="card-header">
                                                <h4>Edit Profile</h4>
                                            </div>
                                            <div class="card-body">
                                                <div class="row">
                                                    <div class="form-group col-md-6 col-12">
                                                        <label>Full Name</label>
                                                        <input type="text" class="form-control" name="name" value="{{ old('name', $user->name) }}" required>
                                                        @error('name')
                                                        <span class="text-danger">{{ $message }}</span>
                                                        @enderror
                                                        <div class="invalid-feedback">
                                                            Please fill in the Full name
                                                        </div>
                                                    </div>
                                                    <div class="form-group col-md-6 col-12">
                                                        <label>Email</label>
                                                        <input type="email" class="form-control" name="email" value="{{ old('email', $user->email) }}" required>
                                                        @error('email')
                                                        <span class="text-danger">{{ $message }}</span>
                                                        @enderror
                                                        <div class="invalid-feedback">
                                                            Please fill in the Email
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="form-group col-md-7 col-12">
                                                        <label>Phone Number</label>
                                                        <input type="tel" name="phone_number" id="phone_number" class="form-control" value="{{ old('phone_number', $user->phone_number) }}">
                                                        @error('phone_number')
                                                        <span class="text-danger">{{ $message }}</span>
                                                        @enderror
                                                        <div class="invalid-feedback">
                                                            Please fill in the Phone Number
                                                        </div>
                                                    </div>
                                                    <div class="form-group col-md-5 col-12">
                                                        <label for="nationality">Nationality</label>
                                                        <input type="text" name="nationality" id="nationality" class="form-control" value="{{ old('nationality', $user->nationality) }}">
                                                        @error('nationality')
                                                        <span class="text-danger">{{ $message }}</span>
                                                        @enderror
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="form-group col-md-7 col-12">
                                                        <label for="state">State</label>
                                                        <input type="text" name="state" id="state" class="form-control" value="{{ old('state', $user->state) }}">
                                                        @error('state')
                                                        <span class="text-danger">{{ $message }}</span>
                                                        @enderror
                                                        <div class="invalid-feedback">
                                                            Please fill in the Phone Number
                                                        </div>
                                                    </div>
                                                    <div class="form-group col-md-5 col-12">
                                                        <label for="address">Address</label>
                                                        <input type="text" name="address" id="address" class="form-control" value="{{ old('address', $user->address) }}">
                                                        @error('address')
                                                        <span class="text-danger">{{ $message }}</span>
                                                        @enderror
                                                    </div>
                                                </div>
                                                <div class="row">
                                                    <div class="form-group col-12">
                                                        <label for="profile_picture">Profile Picture</label>
                                                        <input type="file" name="profile_picture" id="profile_picture" class="form-control-file">
                                                        @error('profile_picture')
                                                        <span class="text-danger">{{ $message }}</span>
                                                        @enderror

                                                        <!-- Display current profile picture -->
                                                        @if ($user->profile_picture)
                                                            <div class="mt-2">
                                                                <img src="{{ asset('storage/profile_pictures/' . $user->profile_picture) }}" alt="Profile Picture" style="width: 100px; height: 100px; border-radius: 50%;">
                                                            </div>
                                                        @endif
                                                    </div>
                                                </div>

                                            </div>
                                            <div class="card-footer text-right">
                                                <button class="btn btn-primary">Update Profile</button>
                                            </div>
                                        </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
       <script>
           document.getElementById('profile-form').addEventListener('submit', function (e) {
               e.preventDefault(); // Prevent the default form submission

               // Get the form data
               const formData = new FormData(this);

               // Send the form data via AJAX
               fetch(this.action, {
                   method: 'POST',
                   body: formData,
                   headers: {
                       'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
                   },
               })
                   .then(response => response.json())
                   .then(data => {
                       if (data.success) {
                           // Show SweetAlert success message
                           swal('Success', 'Profile updated successfully!', 'success');
                       } else {
                           // Show SweetAlert error message
                           swal('Error', 'Something went wrong!', 'error');
                       }
                   })
                   .catch(error => {
                       console.error('Error:', error);
                       swal('Error', 'Something went wrong!', 'error');
                   });
           });
       </script>
    </div>
@endsection
