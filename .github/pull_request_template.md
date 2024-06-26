# Please include a summary of the changes

* File 1 and corresponding changes
* File 2 and corresponding changes

# Any specific logic/part of code you need extra attention on

Explain any specific logic you need special attention on

# Include the Issue number and link

Make sure to link the issue in the github PR UI 

# List/Attach any dependencies/past issues that are required for this change/provide context

# Type of change

- - [ ] Bug fix (non-breaking change which fixes an issue)
- - [ ] New feature (non-breaking change which adds functionality)
- - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- - [ ] This change requires a documentation update
- - [ ] Other (please specify)

# Effort required on reviewers end

- - [ ] Easy
- - [ ] Medium
- - [ ] Hard 

# How Has This Been Tested?

## Bug fix

    Include before and after snapshots/screenshots/changed logs
    
## New feature

    Ensure current test cases pass and include newer test cases if required
    
# CI pipeline result

- - [ ] Pass
- - [ ] Fail
  
  If it fails, explain the reason and whether or not we should ignore the failure
  
# Verify Documentation Update

If applicable, ensure changes to [official documentation](http://vane.arista.com/) are included in the PR by following the steps below:

(1) You can locally make required documentation changes within the [docs](https://github.com/aristanetworks/vane/tree/develop/docs) folder and test them by following these steps:

- `mike deploy test`(or any name you want for the local changes version)
- `mike serve`
  (you will be able to view `test` as an option in the version dropdown)
- Once you have ensured the changes are accurate, execute `mike delete test`(this ensures you do not have any local  version branches which do not exist on gh-pages in the github repo).  

(2) Ensure you have [pre-commit hook](https://pre-commit.com/) installed which will take care of linting checks for documentation before you commit your changes.

(3) Lastly ensure the following jobs pass when you create the PR. These jobs ensure that the changes within your PR do not break the documentation.

- Documentation Testing / Run pre-commit validation hooks (pull_request) 
- Documentation Testing / Build site with no warnings (pull_request)  
   

    
# Additional comments
